
from django.urls import path

# Views 
from .views import (
    # !User - Player
    UserCreateAPIView,
    UserRetriveAPIView,
    UserPartialUpdateAPIView,
    IdRetriveAuthToken,
    PlayerPositionListAPIView,

    # !Match
    MatchListAPIView,
    MatchCreationAPIView,
    FieldFootballTypeListAPIView,
    MatchPlayerRetriveUpdateAPIView,

    # !Field
    FieldListAPIView,
    FieldRetriveAPIView,
)

urlpatterns = [
    # !User
    path('login/', IdRetriveAuthToken.as_view(), name='login'),
    path('signup/', UserCreateAPIView.as_view(), name='signup'),

    # !Player
    path('players/<int:pk>/', UserRetriveAPIView.as_view(), name='player' ),
    path('players/update/<int:pk>/', UserPartialUpdateAPIView.as_view(), name='player_update'),
    path('players/position/', PlayerPositionListAPIView.as_view(), name='player_list_position'),

    # !Match
   path('matches/', MatchListAPIView.as_view(), name='match' ),
   path('matches/create/', MatchCreationAPIView.as_view(), name='match_create'),
   path('fieldfootbaltype/', FieldFootballTypeListAPIView.as_view(), name='fieldfootballtype'),
   path('matches/<int:pk>/',MatchPlayerRetriveUpdateAPIView.as_view(), name='match_retrive'),

   # !Field
   path('fields/', FieldListAPIView.as_view(), name='field_list'),
   path('fields/<int:pk>/', FieldRetriveAPIView.as_view(), name='field_retrive')
]