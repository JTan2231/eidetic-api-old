from django.contrib.auth import login, logout, authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin

class AuthenticationView(APIView,
                         UpdateModelMixin,
                         DestroyModelMixin):

    def post(self, request):
        try:
            user = authenticate(request, username=request.data['username'], password=request.data['password'])
            login(request, user)

            request.session['username'] = user.username
            request.session['user_id'] = user.user_id

            return Response({ 'message': 'logged in' }, status=200)
        except Exception as e:
            print(e)
            return Response({ 'errors': 'Invalid credentials' }, status=400)

class LogoutView(APIView,
                 UpdateModelMixin,
                 DestroyModelMixin):

    def post(self, request):
        logout(request)
        try:
            del request.session['user_id']
            del request.session['username']
            del request.session['auth_token']
        except KeyError:
            pass

        return Response({ 'message': 'logged out' }, status=200)
