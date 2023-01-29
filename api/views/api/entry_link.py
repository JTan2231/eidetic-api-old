from    api.util import extract_text_from_html

# TODO: change this to import nn
#from .nn import create_entry_embedding, query_entries, entry_similarity_ranking, rank_with_average, threshold_query

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin

from api.models import EntryLink
from api.serializers import EntrySerializer

# TODO: Comment these classes/functions
# TODO: This file is filthy. Standardize/clean up some of this stuff

def cutoff(text, cut=250):
    return text[:cut] + '...' if len(text) > cut else text


class EntryLinkView(APIView,
                    UpdateModelMixin,
                    DestroyModelMixin):

    def get(self, request):
        entry_id = request.query_params.get('entry_id')
        try:
            ce_queryset = EntryLink.objects.select_related('centroid', 'branch').filter(centroid__entry_id=entry_id)
        except EntryLink.DoesNotExist:
            return Response([], status=200)

        entries = [ce.branch for ce in ce_queryset]
        read_serializer = EntrySerializer(entries, many=True)

        def data_map(dm):
            return {
                'entry_id': dm['entry_id'],
                'title': dm['title'],
                'timestamp': dm['timestamp'],
                'content': extract_text_from_html(dm['content'])
            }

        data = [data_map(e) for e in read_serializer.data]
        collected_entries = {
            'count': len(entries),
            'entries': data,
        }

        return Response(collected_entries, status=200)
