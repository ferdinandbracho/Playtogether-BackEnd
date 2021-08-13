from os import name
from django.urls import path

# Authentication
from rest_framework.authtoken import views as auth_views

# Views 
from .views import (
    # !User - Player
    UserCreateAPIView,
    UserRetriveAPIView,
    UserPartialUpdateAPIView,

    # !Match
    MatchListAPIView,
)

urlpatterns = [
    # !user
    path('login/', auth_views.obtain_auth_token, name='login'),
    path('signup/', UserCreateAPIView.as_view(), name='signup'),

    # !player
    path('players/<int:pk>', UserRetriveAPIView.as_view(), name='player' ),
    path('players/update/<int:pk>', UserPartialUpdateAPIView.as_view(), name='player_update'),

    # !Mathc
   path('matches/', MatchListAPIView.as_view(), name='match' ),
]