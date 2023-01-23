import io
import json
import string
import requests
import datetime

from zipfile import ZipFile

from api.util import extract_text_from_html

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

from api.models import Entry, User, Collection, CollectionEntry
from api.serializers import EntrySerializer, UserSerializer, CollectionSerializer, CollectionEntrySerializer

class UserView(APIView,
               UpdateModelMixin,
               DestroyModelMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_id = request.query_params.get('user_id')
        if user_id:
            try:
                queryset = User.objects.get(user_id=user_id)
            except User.DoesNotExist:
                return Response({ 'errors': 'This entry does not exist' }, status=400)

            read_serializer = UserSerializer(queryset)

        else:
            queryset = User.objects.all()

            read_serializer = UserSerializer(queryset, many=True)

        return Response(read_serializer.data)
