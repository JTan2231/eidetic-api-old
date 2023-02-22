from api.util import extract_text_from_html

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin

from django.contrib.auth.mixins import LoginRequiredMixin

from api.models import Entry
from api.serializers import EntrySerializer

from api.engine.centroid import create_entries

# TODO: Comment these classes/functions
# TODO: This file is filthy. Standardize/clean up some of this stuff

def cutoff(text, cut=250):
    return text[:cut] + '...' if len(text) > cut else text

class EntryView(APIView,
                UpdateModelMixin,
                DestroyModelMixin,
                LoginRequiredMixin):


    def get_single_entry(self, id):
        try:
            queryset = Entry.objects.get(entry_id=id)
        except Entry.DoesNotExist:
            return Response({ 'errors': 'This entry does not exist' }, status=400)

        read_serializer = EntrySerializer(queryset)
        data = read_serializer.data
        data = {
            'entry_id': data['entry_id'],
            'title': data['title'],
            'timestamp': data['timestamp'],
            'content': extract_text_from_html(read_serializer.data['content']),
        }

        return Response([data], status=200)

    def get_all_entries(self, request):
        """
        Get all entries under a user's ID
        """

        user_id = request.session['user_id']
        try:
            queryset = Entry.objects.filter(user_id=user_id)
        except Entry.DoesNotExist:
            return Response([], status=200)

        read_serializer = EntrySerializer(queryset, many=True)
        entries = [{
            'entry_id': data['entry_id'],
            'title': data['title'],
            'timestamp': data['timestamp'],
            'content': extract_text_from_html(data['content']),
        } for data in read_serializer.data]

        return Response(entries, status=200)

    def get(self, request):
        entry_id = request.query_params.get('entry_id')

        if entry_id is not None:
            return self.get_single_entry(entry_id)
        else:
            return self.get_all_entries(request)

class CreateEntryView(APIView,
                      LoginRequiredMixin):

    def post(self, request):
        new_entry = request.data

        create_entries(request, [new_entry])

        return Response({ 'message': 'todo' }, status=200)

class DeleteEntryView(APIView,
                      LoginRequiredMixin):
    def post(self, request):
        try:
            Entry.objects.get(pk=request.data['entry_id'], user_id=request.session['user_id']).delete()

            return Response({}, status=200)
        except Exception as e:
            return Response({ 'errors': e }, status=400)
