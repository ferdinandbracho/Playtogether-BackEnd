
from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

#!Models
from .models import (
    Field,
    FootballType,
    Match,
    Player,
    Administrator,
    Position,
    Service,
) 
from django.contrib.auth.models import User

# !Serializers 
from .serializers import (
    # !User - Player - FieldlAdmin
    UserModelSerializer,
    UserPlayerRetriveModelSerializer,
    UserPlayerPartialUpdateModelSerializer,
    PlayerPositionModelSerializer,
    UserOrganizedMatchesModelSerializer,
    FieldAdminCreateModelSerializer,
    UserFieldAdminRetriveModelSerializer,

    # !match
    MatchListModelSerializer,
    MatchCreationModelSerializer,
    MatchTeamPlayerModelSerializer,

    # !Field
    FieldListModelSerializer,
    FieldRetriveModelSerializer,
    FootballTypeRetriveModelSerializer,
    FieldServicesListModelSerializer,
)

# !User - Player - FieldAdmin
class IdRetriveAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        model = Player
        if user.is_staff:
            model = Administrator
        instance_photo = model.objects.get(user=user.pk)

        return Response({
            'token': token.key,
            'user_id': user.pk,
            'player_photo' : str(instance_photo.photo),
            'field_admin' : user.is_staff,
        })

    # ?User Player 
class UserPlayerCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserModelSerializer

class UserRetriveAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserPlayerRetriveModelSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

class UserPlayerPartialUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPlayerPartialUpdateModelSerializer
    http_method_names=['get','patch','put']
    parser_classes = [FormParser, MultiPartParser]
    permission_classes = [IsAuthenticated]

class UserOrganizedMatchesAPIView(generics.ListAPIView):
    queryset = Match.objects.all()
    serializer_class = UserOrganizedMatchesModelSerializer

    def get_queryset(self):
        return Match.objects.filter(organizer=self.kwargs['pk'])

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data.insert(0,{'total_matches_organized': len(response.data)})
        return response
    
class PlayerPositionListAPIView(generics.ListAPIView):
    queryset = Position.objects.all()
    serializer_class = PlayerPositionModelSerializer

    # ?FieldAdmin
class UserFielAdminCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = FieldAdminCreateModelSerializer

class UserFieldAdminRetriveAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserFieldAdminRetriveModelSerializer
    permission_classes = [IsAuthenticated]

class UserFieldAdminFieldPartialUpdateAPIView(generics.RetrieveUpdateAPIView):
    pass

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

class FootballTypeListAPIView(generics.ListAPIView):
    queryset = FootballType.objects.all()
    serializer_class = FootballTypeRetriveModelSerializer

class FieldServiceListAPIView(generics.ListAPIView):
    queryset = Service.objects.all()
    serializer_class = FieldServicesListModelSerializer

