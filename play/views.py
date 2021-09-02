
from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
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
    UserRetriveModelSerializer,
    UserPartialUpdateModelSerializer,
    PlayerPositionModelSerializer,
    UserOrganizedMatchesModelSerializer,

    # !match
    MatchListModelSerializer,
    MatchCreationModelSerializer,
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
        player_photo = Player.objects.get(user=user.pk)

        return Response({
            'token': token.key,
            'user_id': user.pk,
            'player_photo' : str(player_photo.photo),
        })

class UserRetriveAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserRetriveModelSerializer
    permission_classes = [IsAuthenticated]

class UserPartialUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPartialUpdateModelSerializer
    http_method_names=['get','patch','put']
    parser_classes = [FormParser, MultiPartParser]
    permission_classes = [IsAuthenticated]

class UserOrganizedMatchesAPIView(generics.ListAPIView):
    queryset = Match.objects.all()
    serializer_class = UserOrganizedMatchesModelSerializer

    def get_queryset(self):
        return Match.objects.filter(organizer=self.request.user.id)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data.insert(0,{'total_matches_organized': len(response.data)})
        return response
    
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

        filters['active'] = True
        return self.queryset.filter(**filters).order_by('date', 'time')

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data.insert(0,{'total_matches': len(response.data)})
        return response
    
class MatchCreationAPIView(generics.CreateAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchCreationModelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

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

