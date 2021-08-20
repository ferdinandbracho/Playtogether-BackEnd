
from rest_framework import generics, serializers
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

#!Models
from .models import (
    Field,
    Match,
    Player,
    Position,
) 
from django.contrib.auth.models import User

# !Serializers 
from .serializers import (
    # !User - Player
    UserModelSerializer,
    UserListModelSerializer,
    UserPartialUpdateModelSerializer,
    UserPhotoModelSerializer,
    PlayerPositionModelSerializer,

    # !match
    MatchListModelSerializer,
    FieldRetriveModelSerializer,

    # !Field
    FieldListModelSerializer,
)

# !User - Player 
class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserModelSerializer

class IdRetriveAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk
        })

class UserRetriveAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserListModelSerializer
    permission_classes = [IsAuthenticated]

class UserPartialUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPartialUpdateModelSerializer
    http_method_names=['get','patch','put']
    parser_classes = [FormParser, MultiPartParser]
    permission_classes = [IsAuthenticated]

class PlayerPhotoRetriveAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserPhotoModelSerializer
    permission_classes = [IsAuthenticated]

class PlayerPositionListAPIView(generics.ListAPIView):
    queryset = Position.objects.all()
    serializer_class = PlayerPositionModelSerializer

# !Match
class MatchListAPIView(generics.ListAPIView):
    queryset =  Match.objects.all()
    serializer_class = MatchListModelSerializer

    def get_queryset(self):
        return self.queryset.filter(active=True).order_by('date', 'time')

# !Field 
class FieldListAPIView(generics.ListAPIView):
    queryset = Field.objects.all()
    serializer_class = FieldListModelSerializer

class FieldRetriveAPIView(generics.RetrieveAPIView):
    queryset = Field.objects.all()
    serializer_class = FieldRetriveModelSerializer