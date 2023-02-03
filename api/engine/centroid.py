import pickle
import requests
import datetime

import numpy as np

from api.engine.compute import rank
from api.engine.cluster import create_clusters

from api.util import extract_text_from_html

from rest_framework.response import Response

from api.models import Entry, EntryLink, Embedding
from api.serializers import EntrySerializer

def fetch_embeddings(text):
    # TODO: replace with ML_API variable
    res = requests.post('http://localhost:5000/get-embedding', json={ 'text': text }).json()
    embedding = np.array([np.array([float(i) for i in s]) for s in res['embedding']])
    mask = np.array([np.array([bool(s)]) for s in res['mask']])

    return embedding, mask

def pad(m, l):
    return np.concatenate([m, np.zeros([max(l - m.shape[0], 0), m.shape[1]], np.float32)])

def create_entry_links(centroid, embedding_matrix, threshold=0.5):
    candidate_embeddings = Embedding.objects.filter(user=centroid.user).exclude(entry__entry_id=centroid.pk)

    if len(candidate_embeddings) == 0:
        return

    cand_embedding_map = { embedding.entry.pk: [] for embedding in candidate_embeddings }
    cand_mask_map = { k: [] for k in cand_embedding_map.keys() }
    cand_entries = { k: None for k in cand_embedding_map.keys() }
    MAXLEN = 0
    for ce in candidate_embeddings:
        cand_embedding_map[ce.entry.pk].append(pickle.loads(ce.embedding))
        cand_mask_map[ce.entry.pk].append(pickle.loads(ce.mask))
        if cand_entries[ce.entry.pk] is None:
            cand_entries[ce.entry.pk] = ce.entry

        MAXLEN = max(MAXLEN, len(cand_embedding_map[ce.entry.pk]))

    cand_entries = [v for _, v in cand_entries.items()]

    cand_embedding_matrices = np.array([np.vstack(pad(np.array(cand_embedding_map[k]), MAXLEN)) for k in cand_embedding_map.keys()])
    cand_embedding_matrices = np.transpose(cand_embedding_matrices, [0, 2, 1])

    cand_mask_matrices = np.array([np.vstack(pad(np.array(cand_mask_map[k]), MAXLEN)) for k in cand_mask_map.keys()])
    cand_mask_matrices = np.transpose(cand_mask_matrices, [0, 2, 1])

    scores = rank(embedding_matrix, cand_embedding_matrices, cand_mask_matrices, return_scores=True)

    new_links = []
    for s in scores:
        # NOTE: there need to be 2 rows for each edge for undirectedness
        if s[0] > threshold:
            new_links.append(EntryLink(
                centroid=centroid,
                branch=cand_entries[s[1]],
                user=centroid.user
            ))

            new_links.append(EntryLink(
                centroid=cand_entries[s[1]],
                branch=centroid,
                user=centroid.user
            ))

    new_links = EntryLink.objects.bulk_create(new_links)
    print(f'{len(new_links)} new edges created!')

def create_entries(request, new_entries):
    user_id = request.session['user_id']

    for i, new_entry in enumerate(new_entries):
        print(f'{i+1} of {len(new_entries)}')

        new_entry['user'] = user_id
        new_entry['timestamp'] = datetime.datetime.now().isoformat()

        if len(new_entry['title']) == 0:
            new_entry['title'] = ' '.join(new_entry['content'].split(' ')[:2]).strip()

        create_serializer = EntrySerializer(data=new_entry)

        if create_serializer.is_valid():
            entry_object = create_serializer.save()

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

            create_entry_links(entry_object, embedding_matrix)

            entry_count = Entry.objects.all().count()
            if entry_count > 1:
                create_clusters(user_id, entry_count, embedding_matrix, entry_object.pk)

        else:
            print(create_serializer.errors)
            return Response(create_serializer.errors, status=400)
