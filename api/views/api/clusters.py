from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin

from django.contrib.auth.mixins import LoginRequiredMixin

from api.models import ClusterLink

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

    def get_clustered_entries(self, request):
        """
        Get all clusters under a user's ID
        """

        user_id = request.session['user_id']
        try:
            queryset = ClusterLink.objects.select_related('cluster', 'entry').filter(user_id=user_id)
        except ClusterLink.DoesNotExist:
            return Response([], status=200)

        clustered_entries = { cl.cluster.pk: [] for cl in queryset }
        for cl in queryset:
            clustered_entries[cl.cluster.pk].append(self.entry_to_dict(cl.entry))

        clustered_entries = [v for v in clustered_entries.values()]

        return Response(clustered_entries, status=200)

    def get(self, request):
        return self.get_clustered_entries(request)
