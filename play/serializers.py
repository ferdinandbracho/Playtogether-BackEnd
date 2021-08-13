from rest_framework import serializers
from django.db.models.aggregates import Count
from django.db import IntegrityError

# !Django-Countries
from django_countries.serializer_fields import CountryField

# !Models
from .models import (
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
        fields = ['first_name', 'last_name','date_joined','players']

    # ?User_Profile Update
class PlayerPartialUpdateModelSerializer(serializers.ModelSerializer):
    photo = serializers.CharField(allow_blank=True)
    nationality = CountryField(name_only=True)
    class Meta:
        model = Player
        fields = ['photo','gender','nationality','position']

class UserPartialUpdateModelSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    class Meta:
        model = User
        fields = ['username','first_name','last_name', 'email']

class UserPartialUpdateModelSerializer(serializers.ModelSerializer):
    user_data = UserPartialUpdateModelSerializer(source='*')
    player_data = PlayerPartialUpdateModelSerializer(source='players')

    class Meta:
        model = User
        fields = ['user_data','player_data']

    def update(self, instance, validated_data):
        player_validated = validated_data.pop('players')
        player = instance.players

        if User.objects.filter(username=validated_data.get('username')).exists():
            raise serializers.ValidationError("Ese nombre de usuario ya fue tomado. Intenta nuevamente!")
        else:
            instance.username = validated_data.get('username', instance.username)   

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()

        player.gender = player_validated.get('gender',player.gender)
        player.nationality = player_validated.get('nationality',player.nationality)
        player.position = player_validated.get('position',player.position)
        player.save()

        return instance

# !Match
class MatchListModelSerializer(serializers.ModelSerializer):
    field = serializers.CharField(read_only=True)
    class Meta:
        model = Match
        fields = ['field','date']