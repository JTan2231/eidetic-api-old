import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

class Entry(models.Model):
    entry_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('user', on_delete=models.CASCADE)

    title = models.TextField(default='untitled')
    content = models.TextField()

    timestamp = models.DateTimeField(default=now, blank=True, null=True)


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

# TODO: the following class needs to be REWORKED for clusters
#class Collection(models.Model):
#    collection_id = models.AutoField(primary_key=True)
#    user = models.ForeignKey('user', on_delete=models.CASCADE)
#    centroid_entry = models.ForeignKey('entry', on_delete=models.CASCADE)
#    title = models.TextField(default='untitled')
#
#    datetime_created = models.DateTimeField(default=now, blank=True, null=True)
#    datetime_edited = models.DateTimeField(default=now, blank=True, null=True)
#
#    class Meta:
#        db_table = 'collections'

class EntryLink(models.Model):
    entry_link_id = models.AutoField(primary_key=True)

    centroid = models.ForeignKey('entry', on_delete=models.CASCADE, related_name='centroid')
    branch = models.ForeignKey('entry', on_delete=models.CASCADE, related_name='branch')
    user = models.ForeignKey('user', on_delete=models.CASCADE)

    class Meta:
        db_table = 'entry_links'
