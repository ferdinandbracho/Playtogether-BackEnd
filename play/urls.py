
from django.urls import path

# Views 
from .views import (
    # !User - Player
    UserPlayerCreateAPIView,
    UserRetriveAPIView,
    UserPlayerPartialUpdateAPIView,
    IdRetriveAuthToken,
    PlayerPositionListAPIView,
    UserOrganizedMatchesAPIView,

    # !Match
    MatchListAPIView,
    MatchCreationAPIView,
    MatchPlayerRetriveUpdateAPIView,

    # !Field
    FieldListAPIView,
    FieldRetriveAPIView,
    FootballTypeListAPIView,
    FieldServiceListAPIView,

    # !User Manager
    UserFieldManagerCreateAPIView,
    UserFieldManagerRetriveAPIView,
    UserFieldManagerFieldPartialUpdateAPIView,
)

urlpatterns = [
    # !User
    path('login/', IdRetriveAuthToken.as_view(), name='login'),
    path('signup_player/', UserPlayerCreateAPIView.as_view(), name='signup_player'),

    # !User - Player
    path('players/<int:pk>/', UserRetriveAPIView.as_view(), name='player' ),
    path('players/update/<int:pk>/', UserPlayerPartialUpdateAPIView.as_view(), name='player_update'),
    path('players/position/', PlayerPositionListAPIView.as_view(), name='player_list_position'),
    path('players/organized/<int:pk>/',UserOrganizedMatchesAPIView.as_view(), name='player_organized_list'),

    # !Match
   path('matches/', MatchListAPIView.as_view(), name='match' ),
   path('matches/create/', MatchCreationAPIView.as_view(), name='match_create'),
   path('matches/<int:pk>/',MatchPlayerRetriveUpdateAPIView.as_view(), name='match_retrive'),

   # !Field
   path('fields/', FieldListAPIView.as_view(), name='field_list'),
   path('fields/<int:pk>/', FieldRetriveAPIView.as_view(), name='field_retrive'),
   path('footballtypes/',FootballTypeListAPIView.as_view(), name='footballtype_list'),
   path('service/',FieldServiceListAPIView.as_view(), name='service_list'),

    # !User - Manager
    path('signup_field_manager/', UserFieldManagerCreateAPIView.as_view(), name='signup_field_manager'),
    path('field_manager/<int:pk>/', UserFieldManagerRetriveAPIView.as_view(), name='field_manager_retrive' ),
    path('field_manager/update/<int:pk>/', UserFieldManagerFieldPartialUpdateAPIView.as_view(), name='field_manager_update' ),

]