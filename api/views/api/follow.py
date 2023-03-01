from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin

from api.models import User, Follow

class FollowView(APIView,
                 UpdateModelMixin,
                 DestroyModelMixin):

    def get(self, request):
        follower_id = request.session['user_id']
        followee_username = request.GET.get('followee_username', '')

        if len(followee_username) == 0:
            return Response({ 'following': False }, status=200)

        try:
            Follow.objects.get(follower_id=follower_id, followee__username=followee_username)
            return Response({ 'following': True }, status=200)
        except:
            return Response({ 'following': False }, status=200)

    def post(self, request):
        follower_id = request.session['user_id']
        followee_username = request.data['followee_username']

        try:
            follow = Follow.objects.get(follower_id=follower_id, followee__username=followee_username)
            follow.delete()
            return Response({ 'status': 'unfollowed'}, status=200)
        except Exception as e:
            print(e)
            pass

        try:
            followee = User.objects.get(username=followee_username)
        except Exception as e:
            print(e)
            return Response({ 'errors': f'error finding user with username {followee_username}'}, status=400)

        follow = Follow(follower_id=follower_id, followee=followee)
        follow.save()

        print(follow)
        return Response({ 'status': 'followed' }, status=200)
