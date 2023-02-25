from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin

from django.contrib.auth.mixins import LoginRequiredMixin

from api.models import ClusterLink, Entry, User

class ClusterView(APIView,
                  UpdateModelMixin,
                  DestroyModelMixin,
                  LoginRequiredMixin):

    def entry_to_dict(self, entry):
        return {
            'entry_id': entry.entry_id,
            'title': entry.title,
            'timestamp': entry.timestamp,
            'content': entry.content,
        }

    def get_entries(self, user_id):
        try:
            queryset = Entry.objects.filter(user_id=user_id)
        except Entry.DoesNotExist:
            return Response([], status=200)

        entries = [[self.entry_to_dict(e) for e in queryset]]
        if len(entries[0]) == 0:
            entries = []

        return Response(entries, status=200)

    def get_clustered_entries(self, request):
        """
        Get all clusters under a user's ID
        """

        username = request.GET.get('username', '')

        if len(username) > 0:
            try:
                user_id = User.objects.get(username=username).pk
            except Exception as e:
                print(e)
                return Response(['NOUSER'], status=400)
        else:
            user_id = request.session['user_id']
        try:
            queryset = ClusterLink.objects.select_related('cluster', 'entry').filter(user_id=user_id)
        except ClusterLink.DoesNotExist:
            return self.get_entries(user_id)

        if len(queryset) == 0:
            return self.get_entries(user_id)

        clustered_entries = { cl.cluster.pk: [] for cl in queryset }
        for cl in queryset:
            clustered_entries[cl.cluster.pk].append(self.entry_to_dict(cl.entry))

        clustered_entries = [v for v in clustered_entries.values()]

        return Response(clustered_entries, status=200)

    def get(self, request):
        return self.get_clustered_entries(request)
