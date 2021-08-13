from django.db.models import query
from rest_framework import generics, serializers

#!Models
from .models import (
    Match,
    Player,
) 
from django.contrib.auth.models import User

# !Serializers 
from .serializers import (
    # !User - Player
    UserModelSerializer,
    UserListModelSerializer,
    UserPartialUpdateModelSerializer,
    PlayerPartialUpdateModelSerializer,

    # !match
    MatchListModelSerializer,
)

# !User - Player 
class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserModelSerializer

class UserRetriveAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserListModelSerializer

class UserPartialUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPartialUpdateModelSerializer
    http_method_names=['get','patch']

# !Match
class MatchListAPIView(generics.ListAPIView):
    queryset =  Match.objects.all()
    serializer_class = MatchListModelSerializer
    
