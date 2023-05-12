from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin

from api.models import Entry, User, Follow

class FeedView(APIView,
               UpdateModelMixin,
               DestroyModelMixin):

    def get(self, request):
        follower_id = request.session['user_id']

        try:
            following = Follow.objects.filter(follower_id=follower_id).values_list('followee_id')
            following = [f[0] for f in following]

            entries = Entry.objects.filter(user_id__in=following, private=False).values_list('entry_id', 'title', 'content', 'timestamp', 'user__username').order_by('-timestamp')[:50]
            entries = [{
                'entry_id': e[0],
                'title': e[1],
                'content': e[2],
                'timestamp': e[3],
                'username': e[4],
            } for e in entries]

            return Response({ 'entries': [entries] }, status=200)

        except Exception as e:
            print(e)
            return Response([], status=400)
