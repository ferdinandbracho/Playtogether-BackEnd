
from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
import datetime as dt

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
    PlayerPositionModelSerializer,

    # !match
    MatchListModelSerializer,
    MatchCreationModelSerializer,

    # !Field
    FieldListModelSerializer,
    FieldRetriveModelSerializer,
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

class PlayerPositionListAPIView(generics.ListAPIView):
    queryset = Position.objects.all()
    serializer_class = PlayerPositionModelSerializer

# !Match
class MatchListAPIView(generics.ListAPIView):
    queryset =  Match.objects.all()
    serializer_class = MatchListModelSerializer

    def get_queryset(self):
        qs = Match.objects.all()
        for match in qs:
            match.datetime_checker()   

        filters = {}

        category = self.request.query_params.get('category')
        if category:
            filters['category'] = category

        football_type = self.request.query_params.get('football_type')
        if football_type:
            filters['field__football_type__name'] = football_type

        field = self.request.query_params.get('field')
        if field:
            filters['field__name'] = field
        
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            filters['date__range'] = (start_date, end_date)


        filters['active'] = True
        return self.queryset.filter(**filters).order_by('date', 'time')

class MatchCreationAPIView(generics.CreateAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchCreationModelSerializer

# !Field 
class FieldListAPIView(generics.ListAPIView):
    queryset = Field.objects.all()
    serializer_class = FieldListModelSerializer

class FieldRetriveAPIView(generics.RetrieveAPIView):
    queryset = Field.objects.all()
    serializer_class = FieldRetriveModelSerializer
