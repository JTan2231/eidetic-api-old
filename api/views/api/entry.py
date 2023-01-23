import io
import json
import string
import pickle
import requests
import datetime

import numpy as np

from api.engine.compute import rank

from zipfile import ZipFile

from api.util import extract_text_from_html

from django.shortcuts import render
from django.http import FileResponse
from django.contrib.auth.hashers import make_password, check_password

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin

from django.contrib.auth import login
from rest_framework import permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.permissions import IsAuthenticated
from knox.views import LoginView as KnoxLoginView
from knox.auth import TokenAuthentication

from django.db.models import F, Subquery

from api.models import Entry, User, Collection, CollectionEntry, Embedding
from api.serializers import EntrySerializer, UserSerializer, CollectionSerializer, CollectionEntrySerializer, EmbeddingSerializer

# TODO: Comment these classes/functions
# TODO: This file is filthy. Standardize/clean up some of this stuff

def cutoff(text, cut=250):
    return text[:cut] + '...' if len(text) > cut else text

def fetch_embeddings(text):
    res = requests.post('http://localhost:5000/get-embedding', json={ 'text': text }).json()
    embedding = np.array([np.array([float(i) for i in s]) for s in res['embedding']])
    mask = np.array([np.array([bool(s)]) for s in res['mask']])

    return embedding, mask

def get_collection_entries(user_id):
    try:
        collection_entries = CollectionEntry.objects.filter(user=user_id).only('collection', 'entry')

        entry_ids = [ce.entry.entry_id for ce in collection_entries]
        embeddings = Embedding.objects.filter(user=user_id, entry__in=entry_ids)

        e_groups = {}
        m_groups = {}
        for e in embeddings:
            if e_groups.get(e.entry.pk, None) is None:
                e_groups[e.entry.pk] = [(e.token_index, pickle.loads(e.embedding))]
                m_groups[e.entry.pk] = [(e.token_index, pickle.loads(e.mask))]
            else:
                e_groups[e.entry.pk].append((e.token_index, pickle.loads(e.embedding)))
                m_groups[e.entry.pk].append((e.token_index, pickle.loads(e.mask)))

        # please make this clearer dear god
        embeddings = [np.vstack([e[1] for e in sorted(v, key=lambda x: x[0])]) for _, v in e_groups.items()]
        masks = [np.vstack([e[1] for e in sorted(v, key=lambda x: x[0])]) for _, v in m_groups.items()]

    except Exception as e:
        print("error:", e)
        return None

    class obj:
        def __init__(self, c, e, m):
            self.collection = c
            self.embedding = e
            self.mask = m

    return [obj(ce.collection, e, m) for (ce, e, m) in zip(collection_entries, embeddings, masks)]

def create_collection_from_entry(candidate_entry):
    collection_data = {
        'user': candidate_entry.user.pk,
        'centroid_entry': candidate_entry.entry_id,
        'title': candidate_entry.title,
        'datetime_created': datetime.datetime.now().isoformat(),
        'datetime_edited': datetime.datetime.now().isoformat(),
    }

    collection_serializer = CollectionSerializer(data=collection_data)
    collection_id = None
    if collection_serializer.is_valid():
        collection = collection_serializer.save()
        collection_id = CollectionSerializer(collection).data['collection_id']
    else:
        print(collection_serializer.errors)
        return None

    collection_entry = CollectionEntry.objects.create(
        user=candidate_entry.user,
        entry=candidate_entry,
        collection=collection
    )

    return [collection_id, collection_entry.collection_entry_id]

def pad(m, l):
    return np.concatenate([m, np.zeros([max(l - m.shape[0], 0), m.shape[1]], np.float32)])

def determine_collections(candidate_entry, candidate_embedding, candidate_mask, threshold=0.6):
    collection_entries = get_collection_entries(candidate_entry.user)

    # if there's nothing here, create a collection for the entry
    if len(collection_entries) == 0:
        return create_collection_from_entry(candidate_entry)

    MAXLEN = max(ce.embedding.shape[0] for ce in collection_entries)

    embeddings = []
    masks = []
    collection_ids = []

    for ce in collection_entries:
        embeddings.append(pad(ce.embedding, MAXLEN))
        masks.append(pad(ce.mask, MAXLEN))
        collection_ids.append(ce.collection)

    embeddings = np.array(embeddings)
    masks = np.array(masks)

    embedding_matrix = np.transpose(embeddings, axes=[0, 2, 1])
    mask_matrix = np.transpose(masks, axes=[0, 2, 1])

    ranking = rank(candidate_embedding, embedding_matrix, mask_matrix, return_scores=True)
    ranking = [r[1] for r in ranking if r[0] > threshold]

    if len(ranking) == 0:
        return create_collection_from_entry(candidate_entry)

    new_collection_entries = []
    collections = dict()
    for i in ranking:
        if collections.get(collection_entries[i].collection.pk, None) == None:
            new_collection_entries.append(CollectionEntry(
                entry=candidate_entry,
                user=candidate_entry.user,
                collection=collection_entries[i].collection,
            ))

            collections[collection_entries[i].collection.pk] = True

    new_collection_entries = CollectionEntry.objects.bulk_create(new_collection_entries)

def create_entries(new_entries):
    for new_entry in new_entries:
        new_entry['timestamp'] = datetime.datetime.now().isoformat()

        if len(new_entry['title']) == 0:
            new_entry['title'] = new_entry['timestamp']

        create_serializer = EntrySerializer(data=new_entry)

        if create_serializer.is_valid():
            entry_object = create_serializer.save()
            read_serializer = EntrySerializer(entry_object)

            embedding_matrix, mask_matrix = fetch_embeddings(extract_text_from_html(new_entry['content']))

            embeddings = []
            for i in range(embedding_matrix.shape[0]):
                embeddings.append(Embedding(
                    token_index=i,
                    embedding=pickle.dumps(embedding_matrix[i]),
                    mask=pickle.dumps(mask_matrix[i]),
                    user=entry_object.user,
                    entry=entry_object
                ))

            embeddings = Embedding.objects.bulk_create(embeddings)

            # compare against all CollectionEntries
            collections = determine_collections(entry_object, embedding_matrix, mask_matrix)
        else:
            print(create_serializer.errors)
            return Response(create_serializer.errors, status=400)

    return Response({}, status=201)

class EntryView(APIView,
                UpdateModelMixin,
                DestroyModelMixin):

    class GetQueryParams:
        def __init__(self, qp):
            self.id = qp.get('id')
            self.title = qp.get('title')
            self.query = qp.get('query')
            self.user_id = qp.get('user_id')
            self.collection_id = qp.get('collection_id')

            r = qp.get('return')
            self.return_entries = r if r is not None else False

    def get(self, request):

        qp = self.GetQueryParams(request.query_params)

        if qp.id is not None:
            try:
                queryset = Entry.objects.get(entry_id=qp.id)
            except Entry.DoesNotExist:
                return Response({ 'errors': 'This entry does not exist' }, status=400)

            read_serializer = EntrySerializer(queryset)
            data = read_serializer.data
            data = {
                'title': data['title'],
                'timestamp': data['timestamp'],
                'content': extract_text_from_html(read_serializer.data['content']),
            }

            return Response(data, status=200)

class CreateEntryView(APIView,
                UpdateModelMixin,
                DestroyModelMixin):

    #authentication_classes = (TokenAuthentication,)
    #permission_classes = (IsAuthenticated,)

    def post(self, request):
        new_entry = request.data

        return create_entries([new_entry])
