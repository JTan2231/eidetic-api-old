import io
import json
import string
import requests
import datetime

from zipfile import ZipFile

from app.quickstart.util import extract_text_from_html

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
from knox.views import LoginView as KnoxLoginView, LogoutView as KnoxLogoutView
from knox.auth import TokenAuthentication

from app.quickstart.models import Entry, User, Collection, CollectionEntry
from app.quickstart.serializers import EntrySerializer, UserSerializer, CollectionSerializer, CollectionEntrySerializer

class AuthenticationView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        login(request, user)

        res = super().post(request, format=None)
        res.data['user_id'] = user.user_id

        res.set_cookie('auth_token', res.data['token'], samesite='None', secure=True)
        res.set_cookie('username', user.username, samesite='None', secure=True)
        res.set_cookie('user_id', res.data['user_id'], samesite='None', secure=True)

        return res

class LogoutView(KnoxLogoutView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        res = super().post(request, format=format)

        res.delete_cookie('auth_token')
        res.delete_cookie('username')
        res.delete_cookie('user_id')

        return res
