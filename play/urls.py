
from django.urls import path

# Views 
from .views import (
    # !User - Player
    UserCreateAPIView,
    UserRetriveAPIView,
    UserPartialUpdateAPIView,
    IdRetriveAuthToken,
    PlayerPhotoRetriveAPIView,
    PlayerPositionListAPIView,

    # !Match
    MatchListAPIView,
)

urlpatterns = [
    # !User
    path('login/', IdRetriveAuthToken.as_view(), name='login'),
    path('signup/', UserCreateAPIView.as_view(), name='signup'),

    # !Player
    path('players/<int:pk>', UserRetriveAPIView.as_view(), name='player' ),
    path('players/update/<int:pk>', UserPartialUpdateAPIView.as_view(), name='player_update'),
    path('players/photo/<int:pk>', PlayerPhotoRetriveAPIView.as_view(), name='player_photo'),
    path('players/position/', PlayerPositionListAPIView.as_view(), name='player_list_position'),

    # !Match
   path('matches/', MatchListAPIView.as_view(), name='match' ),
]