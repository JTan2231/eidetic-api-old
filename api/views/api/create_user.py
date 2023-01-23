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

# TODO: Comment these classes/functions
# TODO: This file is filthy. Standardize/clean up some of this stuff

class CreateUserView(KnoxLoginView):
    authentication_classes = tuple()
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        if not User.objects.filter(username=request.data['username']).exists():
            try:
                data = request.data
                data['password'] = make_password(data['password'])

                create_serializer = UserSerializer(data=data)

                if create_serializer.is_valid():
                    user_object = create_serializer.save()
                    read_serializer = UserSerializer(user_object)

                    return Response(request.data, status=200)

            except Exception as e:
                print(e)
                return Response(create_serializer.errors, status=400)
        else:
            return Response({ 'errors': 'User with this name already exists' }, status=400)
