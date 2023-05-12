from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

class Entry(models.Model):
    entry_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('user', on_delete=models.CASCADE)

    title = models.TextField(default='untitled')
    content = models.TextField()

    timestamp = models.DateTimeField(default=now, blank=True, null=True)
    private = models.BooleanField(default=False)

    class Meta:
        db_table = 'entries'

class Embedding(models.Model):
    embedding_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('user', on_delete=models.CASCADE)
    entry = models.ForeignKey('entry', on_delete=models.CASCADE)

    token_index = models.IntegerField()

    embedding = models.BinaryField(None, default=b'0')
    mask = models.BinaryField(None, default=b'0')

    class Meta:
        db_table = 'embeddings'

class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'users'

# centroid graph edges
class EntryLink(models.Model):
    entry_link_id = models.AutoField(primary_key=True)

    centroid = models.ForeignKey('entry', on_delete=models.CASCADE, related_name='centroid')
    branch = models.ForeignKey('entry', on_delete=models.CASCADE, related_name='branch')
    user = models.ForeignKey('user', on_delete=models.CASCADE)

    class Meta:
        db_table = 'entry_links'

class Cluster(models.Model):
    cluster_id = models.AutoField(primary_key=True)

    user = models.ForeignKey('user', on_delete=models.CASCADE)
    title = models.TextField()

    class Meta:
        db_table = 'clusters'

class ClusterLink(models.Model):
    cluster_link_id = models.AutoField(primary_key=True)

    cluster = models.ForeignKey('cluster', on_delete=models.CASCADE)
    entry = models.ForeignKey('entry', on_delete=models.CASCADE)
    user = models.ForeignKey('user', on_delete=models.CASCADE)

    class Meta:
        db_table = 'cluster_links'

# TODO: change this?
# probably dangerous but w/e for now
class ClusteringAlgorithm(models.Model):
    clustering_algorithm_id = models.AutoField(primary_key=True)

    user = models.ForeignKey('user', on_delete=models.CASCADE)
    algorithm = models.BinaryField(None, default=b'0')
    cluster_id_mapping = models.BinaryField(None, default=b'0')

    class Meta:
        db_table = 'clustering_algorithms'

class Follow(models.Model):
    follow_id = models.AutoField(primary_key=True)

    follower = models.ForeignKey('user', on_delete=models.CASCADE, related_name='follower')
    followee = models.ForeignKey('user', on_delete=models.CASCADE, related_name='followee')

    class Meta:
        db_table = 'follow'
