import pickle
import numpy as np

from math import sqrt
from api.models import Cluster, Embedding, ClusterLink, ClusteringAlgorithm

from sklearn.cluster import KMeans

# TODO: this has a lot of optimization opportunities
def create_clusters(user_id, entry_count, new_embeddings, new_entry_id):
    try:
        cluster_queryset = Cluster.objects.filter(user_id=user_id)
        cluster_count = len(cluster_queryset)
    except Cluster.DoesNotExist:
        cluster_count = 0

    no_algo = False
    try:
        clustering_algorithm = ClusteringAlgorithm.objects.get(user_id=user_id)
    except ClusteringAlgorithm.DoesNotExist:
        no_algo = True

    count = entry_count
    new_cluster_count = int(sqrt(count))

    # check if new clusters need made
    if new_cluster_count == cluster_count:
        clusterer = pickle.loads(clustering_algorithm.algorithm)
        new_average = np.mean(new_embeddings, axis=0, keepdims=True)
        labels = clusterer.predict(new_average)

        mapping = pickle.loads(clustering_algorithm.cluster_id_mapping)

        new_cluster_link = ClusterLink(cluster_id=mapping[labels[0]], entry_id=new_entry_id, user_id=user_id)
        new_cluster_link.save()

        return

    else:
        try:
            # generate entry-average embeddings for each of the user's entries
            embedding_queryset = Embedding.objects.filter(user_id=user_id)
            average_dict = {}
            for embedding in embedding_queryset:
                entry_id = embedding.entry.pk
                avg = average_dict.get(entry_id, None)
                if avg is None:
                    average_dict[entry_id] = [pickle.loads(embedding.embedding), 1]
                else:
                    average_dict[entry_id] = [avg[0] + pickle.loads(embedding.embedding), avg[1]]

            averages = [v[0]/v[1] for _, v in average_dict.items()]
            averages = [a / np.linalg.norm(a) for a in averages] # normalization step -- is this needed?
        except Embedding.DoesNotExist:
            return

    print(f'creating new clustering algorithm for refitting for {user_id}')
    clusterer = KMeans(n_clusters=new_cluster_count)
    pickled = pickle.dumps(clusterer)

    if no_algo:
        clustering_algorithm = ClusteringAlgorithm(user_id=user_id, algorithm=pickled)
        clustering_algorithm.save()
        print('clustering algorithm created')

    print('refitting clustering algorithm')
    clusterer = clusterer.fit(averages)

    print('refitted')
    clustering_algorithm.algorithm = pickle.dumps(clusterer)

    entry_ids = list(average_dict.keys())
    labels = clusterer.labels_

    assert len(entry_ids) == len(averages)

    clustered_ids = { label: [] for label in labels }
    for i in range(len(entry_ids)):
        clustered_ids[labels[i]].append(entry_ids[i])

    # clear out old clusters in database to make room for new ones
    ClusterLink.objects.filter(user=user_id).delete()
    Cluster.objects.filter(user=user_id).delete()

    # create clusters in DB
    new_clusters = [Cluster(user_id=user_id, title='untitled') for _ in range(new_cluster_count)]
    new_clusters = Cluster.objects.bulk_create(new_clusters)

    new_cluster_links = []
    for k in clustered_ids.keys():
        for id in clustered_ids[k]:
            new_cluster_links.append(ClusterLink(
                cluster=new_clusters[k],
                entry_id=id,
                user_id=user_id,
            ))

    new_cluster_links = ClusterLink.objects.bulk_create(new_cluster_links)

    cluster_id_mapping = { label: new_clusters[label].pk for label in labels }
    clustering_algorithm.cluster_id_mapping = pickle.dumps(cluster_id_mapping)
    clustering_algorithm.save()
