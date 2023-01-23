import io
import json
import string
import requests
import datetime

from zipfile import ZipFile

from    api.util import extract_text_from_html

# TODO: change this to import nn
#from .nn import create_entry_embedding, query_entries, entry_similarity_ranking, rank_with_average, threshold_query

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

from    api.models import Entry, User, Collection, CollectionEntry
from    api.serializers import EntrySerializer, UserSerializer, CollectionSerializer, CollectionEntrySerializer

# TODO: Comment these classes/functions
# TODO: This file is filthy. Standardize/clean up some of this stuff

def cutoff(text, cut=250):
    return text[:cut] + '...' if len(text) > cut else text

class CollectionView(APIView,
                     UpdateModelMixin,
                     DestroyModelMixin):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_id = request.query_params.get('user_id')
        try:
            collections_queryset = Collection.objects.filter(user_id=user_id)
        except Collection.DoesNotExist:
            return Response([], status=200)

        read_serializer = CollectionSerializer(collections_queryset, many=True)

        return Response(read_serializer.data, status=200)

    def post(self, request):
        return Response({ 'errors': 'Not yet implemented' }, status=405)

        #############################
        # TODO                      #
        #############################

        """

        data = request.data

        if Collection.objects.filter(centroid_entry_id=data['entry_id']).exists():
            return Response({ 'errors': 'Collection started with this entry already exists' }, status=400)

        # prune the user's entries to figure out which belong in the collection

        all_entries_queryset = Entry.objects.filter(user_id=data['user_id'])
        all_entries = EntrySerializer(all_entries_queryset, many=True).data

        centroid = None
        candidates = ([], [], [])
        for entry in all_entries:
            if entry['id'] == data['entry_id']:
                centroid = to_bytesio(entry['embedding'])

            candidates[0].append(entry['id'])
            candidates[1].append(to_bytesio(entry['embedding']))
            candidates[2].append(to_bytesio(entry['mask']))

        ids, embeddings, masks = candidates
        filtered_indices = threshold_query(centroid, embeddings, masks)
        filtered_ids = [data['entry_id']] + [ids[i] for i in filtered_indices]

        def get_title(title):
            return title if len(title) > 0 else datetime.datetime.now().isoformat()

        # create the collection
        try:
            collection_data = {
                'user_id': data['user_id'],
                'centroid_entry': data['entry_id'],
                'title': get_title(data['title']),
                'datetime_created': datetime.datetime.now().isoformat(),
                'datetime_edited': datetime.datetime.now().isoformat(),
            }

            collection_serializer = CollectionSerializer(data=collection_data)
            collection_id = None
            if collection_serializer.is_valid():
                collection = collection_serializer.save()
                collection_id = CollectionSerializer(collection).data['collection_id']
            else:
                return Response(collection_serializer.errors, status=400)
        except Exception as e:
            print(e)
            return Response({ 'errors': 'Error creating collection' }, status=400)

        # TODO: is there a better way of doing this? feels inefficient
        # create the CollectionEntries to link the entries to the collection
        collection_entries = []
        user = User(user_id=data['user_id'])
        for fid in filtered_ids:
            collection_entries.append(CollectionEntry(
                id=Entry(id=fid),
                user_id=user,
                collection_id=collection,
            ))

        collection_entries = CollectionEntry.objects.bulk_create(collection_entries)

        return Response({ 'num_entries': len(collection_entries) }, status=200)
        """
