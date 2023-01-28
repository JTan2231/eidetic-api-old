from django.contrib.auth.hashers import make_password
from rest_framework.response import Response

from django.contrib.auth import login
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin

from api.models import User
from api.serializers import UserSerializer

# TODO: Comment these classes/functions
# TODO: This file is filthy. Standardize/clean up some of this stuff

class CreateUserView(APIView,
                     UpdateModelMixin,
                     DestroyModelMixin):
    authentication_classes = tuple()
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        if not User.objects.filter(username=request.data['username']).exists():
            try:
                data = request.data
                data['password'] = make_password(data['password'])

                create_serializer = UserSerializer(data=data)

                if create_serializer.is_valid():
                    user_object = create_serializer.save()
                    login(request, user_object)

                    return Response(request.data, status=200)

            except Exception as e:
                print(e)
                return Response(create_serializer.errors, status=400)
        else:
            return Response({ 'errors': 'User with this name already exists' }, status=400)
