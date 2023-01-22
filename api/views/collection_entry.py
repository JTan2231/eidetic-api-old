import io
import json
import string
import requests
import datetime

from zipfile import ZipFile

from    app.quickstart.util import extract_text_from_html

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

from    app.quickstart.models import Entry, User, Collection, CollectionEntry
from    app.quickstart.serializers import EntrySerializer, UserSerializer, CollectionSerializer, CollectionEntrySerializer

# TODO: Comment these classes/functions
# TODO: This file is filthy. Standardize/clean up some of this stuff

def cutoff(text, cut=250):
    return text[:cut] + '...' if len(text) > cut else text


class CollectionEntryView(APIView,
                          UpdateModelMixin,
                          DestroyModelMixin):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_id = request.query_params.get('user_id')
        collection_id = request.query_params.get('collection_id')
        try:
            ce_queryset = CollectionEntry.objects.select_related('entry', 'collection').filter(user_id=user_id, collection_id=collection_id)
        except Collection.DoesNotExist:
            return Response([], status=200)

        collection = ce_queryset[0].collection
        entries = [ce.entry for ce in ce_queryset]
        read_serializer = EntrySerializer(entries, many=True)

        def data_map(dm):
            return {
                'id': dm['entry_id'],
                'title': dm['title'],
                'timestamp': dm['timestamp'],
                'text_preview': cutoff(extract_text_from_html(dm['content']))
            }

        data = [data_map(e) for e in read_serializer.data]
        collected_entries = [{
            'collection_id': collection.collection_id,
            'title': collection.title,
            'datetime_created': collection.datetime_created,
            'count': len(entries),
            'entries': data,
        }]

        return Response(collected_entries, status=200)
