from pkg_resources import require
from rest_framework.fields import ImageField
from rest_framework.generics import DestroyAPIView
from playtogether.settings import ALLOWED_HOSTS
from rest_framework import serializers
from django.db.models.aggregates import Count
from django.db import IntegrityError

# !Django-Countries
from django_countries.serializer_fields import CountryField

# !Models
from .models import (
    Field,
    Player,
    Match,
    Position,
)
from django.contrib.auth.models import User

# !User - Player
    # ?User Creation
class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
        ]
        extra_kwargs = {'password':{'write_only' : True}}

    def create(self, validate_data):
        user = User.objects.create_user(**validate_data)
        return user

    # ?User_Player Profile 
class PlayerModelSerializer(serializers.ModelSerializer):
    position = serializers.CharField()
    matches = serializers.SerializerMethodField()
    fields_count = serializers.SerializerMethodField()
    matches_count = serializers.SerializerMethodField()
    photo = serializers.ImageField(use_url=True)

    def get_matches(self, obj):
        qs = Match.objects.filter(team__players=obj).order_by('date')
        result = MatchListModelSerializer(qs, many=True).data
        return result 

    def get_matches_count(self, obj):
        return Match.objects.filter(team__players=obj).count()

    def get_fields_count(self, obj):
        return Match.objects.filter(team__players=obj).aggregate(Count('field_id', distinct=True))['field_id__count']
    
    class Meta:
        model = Player
        fields= ['photo','dominant_food','position','matches','matches_count','fields_count'] 

class UserListModelSerializer(serializers.ModelSerializer):
    players = PlayerModelSerializer()

    class Meta:
        model = User
        fields = ['username','first_name', 'last_name','date_joined','players']

    # ?User_Profile Update
class PlayerPartialUpdateModelSerializer(serializers.ModelSerializer):
    nationality = CountryField(name_only=True)
    photo = serializers.ImageField(use_url=True)

    class Meta:
        model = Player
        fields = ['gender','nationality','position','photo']

class UserPartialUpdateModelSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = User
        fields = ['username','first_name','last_name', 'email']

class UserPartialUpdateModelSerializer(serializers.ModelSerializer):
    user_data = UserPartialUpdateModelSerializer(source='*', required=False)
    player_data = PlayerPartialUpdateModelSerializer(source='players', required=False)

    class Meta:
        model = User
        fields = ['user_data','player_data']

    def update(self, instance, validated_data):
        player_validated = validated_data.pop('players')
        player = instance.players

        username = User.objects.filter(username=validated_data.get('username'))

        if username.exists() and instance.username != validated_data.get('username'):
            raise serializers.ValidationError("Ese nombre de usuario ya fue tomado. Intenta nuevamente!")
        else:
            instance.username = validated_data.get('username', instance.username)    

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()

        player.gender = player_validated.get('gender',player.gender)
        player.nationality = player_validated.get('nationality',player.nationality)
        player.position = player_validated.get('position',player.position)
        player.photo = player_validated.get('photo',player.photo)
        player.save()

        return instance

        # ? User photo retrive for navbar
class PlayerPhotoModelSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(use_url=True)

    class Meta:
        model = Player
        fields = ['photo']

class UserPhotoModelSerializer(serializers.ModelSerializer):
    player_photo = PlayerPhotoModelSerializer(source='players')

    class Meta:
        model = User
        fields = ['id','player_photo']

class PlayerPositionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'

# !Match
class FieldListModelSerializer(serializers.ModelSerializer):
    football_type = serializers.CharField()
    class Meta:
        model = Field
        fields = ['name','football_type']

class MatchListModelSerializer(serializers.ModelSerializer):
    field = FieldListModelSerializer()

    class Meta:
        model = Match
        fields = ['id','field','date','time','category']