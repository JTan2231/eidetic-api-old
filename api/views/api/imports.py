import json
import requests

from .entry import create_entries

# TODO: change this to import nn
#from .nn import create_entry_embedding, query_entries, entry_similarity_ranking, rank_with_average, threshold_query

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin

# TODO: Comment these classes/functions
# TODO: This file is filthy. Standardize/clean up some of this stuff

def cutoff(text, cut=250):
    return text[:cut] + '...' if len(text) > cut else text

class ImportView(APIView,
                 UpdateModelMixin,
                 DestroyModelMixin):

    def post(self, request):
        data = request.data
        user_id = request.session['user_id']

        if data['channel'] is None:
            return Response({ 'errors': 'Requires channel' }, status=400)

        url = 'http://api.are.na/v2/channels/' + data['channel'] + '?per=100'
        channel = json.loads(requests.get(url).content)

        if channel.get('code', None) is not None and channel['code'] >= 400:
            return Response({ 'errors': 'invalid channel url' }, status=channel['code'])

        contents = [{
            'content': c['content'],
            'user': user_id,
            'title': '',
        } for c in channel['contents'] if c['class'] == 'Text']

        return create_entries(request, contents)

