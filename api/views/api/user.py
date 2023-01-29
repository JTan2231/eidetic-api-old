from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin

from rest_framework.permissions import IsAuthenticated

from knox.auth import TokenAuthentication

from api.models import User
from api.serializers import UserSerializer

class UserView(APIView,
               UpdateModelMixin,
               DestroyModelMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_id = request.query_params.get('user_id')
        if user_id:
            try:
                queryset = User.objects.get(user_id=user_id)
            except User.DoesNotExist:
                return Response({ 'errors': 'This entry does not exist' }, status=400)

            read_serializer = UserSerializer(queryset)

        else:
            queryset = User.objects.all()

            read_serializer = UserSerializer(queryset, many=True)

        return Response(read_serializer.data)
