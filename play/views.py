
from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
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
    FieldFootbalTypeModelSerializer,
    MatchTeamPlayerModelSerializer,


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
        # for match in qs:
            # match.datetime_checker()   

        filters = {}

        category = self.request.GET.getlist('category')
        if category:
            filters['category__in'] = category

        football_type = self.request.GET.getlist('football_type')
        if football_type:
            filters['field__football_type__name__in'] = football_type

        field = self.request.GET.getlist('field')
        if field:
            filters['field__name__in'] = field
        
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            filters['date__range'] = (start_date, end_date)

        now = dt.datetime.today()
        # filters['active'] = True
        return self.queryset.filter(**filters).order_by('date', 'time').filter(date__gte=now, time__gte=now)

class MatchCreationAPIView(generics.CreateAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchCreationModelSerializer

class MatchPlayerRetriveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchTeamPlayerModelSerializer
    http_method_names=['get','patch'] 
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):

        match = Match.objects.get(id=self.kwargs.get('pk'))
        match.datetime_checker()
        return super().get_queryset()


# !Field 
class FieldListAPIView(generics.ListAPIView):
    queryset = Field.objects.all()
    serializer_class = FieldListModelSerializer

class FieldRetriveAPIView(generics.RetrieveAPIView):
    queryset = Field.objects.all()
    serializer_class = FieldRetriveModelSerializer

class FieldFootballTypeListAPIView(generics.ListAPIView):
    queryset = Field.objects.all()
    serializer_class = FieldFootbalTypeModelSerializer
