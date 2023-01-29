import json
import requests

from .entry import create_entries

# TODO: change this to import nn
#from .nn import create_entry_embedding, query_entries, entry_similarity_ranking, rank_with_average, threshold_query

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin

from rest_framework.permissions import IsAuthenticated
from knox.auth import TokenAuthentication

from api.models import User

# TODO: Comment these classes/functions
# TODO: This file is filthy. Standardize/clean up some of this stuff

def cutoff(text, cut=250):
    return text[:cut] + '...' if len(text) > cut else text

class ImportView(APIView,
                 UpdateModelMixin,
                 DestroyModelMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data

        if data['channel'] is None or data['user_id'] is None:
            return Response({ 'errors': 'Requires user_id and channel' }, status=400)

        user = User.objects.filter(user_id=data['user_id']).first()

        url = 'http://api.are.na/v2/channels/' + data['channel'] + '?per=100'
        channel = json.loads(requests.get(url).content)

        if channel.get('code', None) is not None and channel['code'] >= 400:
            return Response({ 'errors': 'invalid channel url' }, status=channel['code'])

        contents = [{
            'content': c['content'],
            'user': user.pk,
            'title': '',
        } for c in channel['contents'] if c['class'] == 'Text']

        return create_entries(contents)

