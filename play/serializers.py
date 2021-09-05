
from rest_framework import serializers
from django.db.models.aggregates import Count
import datetime as dt
from .models import validate_media_size

# !Django-Countries
from django_countries.serializer_fields import CountryField

# !Models
from .models import (
    Field,
    FootballType,
    Player,
    Match,
    Position,
    Service,
    Team,
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
            'password'
        ]
        extra_kwargs = {'password':{'write_only' : True}}

    def create(self, validate_data):
        user = User.objects.create_user(**validate_data)
        player = Player.objects.create(user=user)
        player.save()
        return user

    # ?User_Player Profile 
class PlayerModelSerializer(serializers.ModelSerializer):
    player_id = serializers.CharField(source='id')
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
        fields= ['player_id','dominant_food','position','photo','matches','matches_count','fields_count'] 

class UserRetriveModelSerializer(serializers.ModelSerializer):
    players = PlayerModelSerializer()

    class Meta:
        model = User
        fields = ['username','first_name', 'last_name','date_joined','players']


    # ?User_Profile Update
class PlayerPartialUpdateModelSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(use_url=True, validators=[validate_media_size])
    gender = serializers.ChoiceField(choices=Player.GENDER)

    class Meta:
        model = Player
        fields = ['gender','position','photo']

class UserPartialUpdateModelSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.EmailField(read_only=True)

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
        validated_data
        user = self.context['request'].user.id
        if user != instance.id:
            raise serializers.ValidationError({"Fail":"Not your profile"})

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
        player.position = player_validated.get('position',player.position)
        player.photo = player_validated.get('photo',player.photo)
        player.save()

        return instance

class PlayerPositionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'

# !Field
class FootballTypeRetriveModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FootballType
        fields = '__all__'

class FieldRetriveModelSerializer(serializers.ModelSerializer):
    address = serializers.CharField()
    football_type = FootballTypeRetriveModelSerializer()
    services = serializers.StringRelatedField(many=True, source='fields_services',read_only=True)
    class Meta:
        model = Field
        fields = ['id','name','rent_cost','address','football_type','services']

class FieldListModelSerializer(serializers.ModelSerializer):
    address = serializers.CharField()
    football_type = serializers.CharField()

    class Meta:
        model = Field
        fields = ['id','name','address','football_type']

# !Match
class FieldSelectedListModelSerializer(serializers.ModelSerializer):
    football_type = serializers.CharField()
    class Meta:
        model = Field
        fields = ['name','football_type']

class MatchListModelSerializer(serializers.ModelSerializer):
    field = FieldSelectedListModelSerializer()
    date = serializers.DateField(required=True, input_formats=["%d-%m-%Y"])
    time = serializers.TimeField(required=True, input_formats=['%H:%M'])
    places_available= serializers.SerializerMethodField()

    def get_places_available(self, obj):
        registered =  Match.objects.filter(id=obj.id).aggregate(registered=Count('team__players'))['registered']
        max_player = obj.field.football_type.max_players
        return max_player - registered

    class Meta:
        model = Match
        fields = ['id','field','date','time','category','places_available' ]

class MatchCreationModelSerializer(serializers.ModelSerializer):
    date = serializers.DateField(required=True, input_formats=["%d-%m-%Y"])
    time = serializers.TimeField(required=True, input_formats=['%H:%M'])
    category = serializers.ChoiceField(choices=Match.CATEGORY)

    class Meta:
        model = Match
        fields = ['id','field','date','time','category']

    def create(self, validated_data):
        duration = FootballType.objects.get(fields=validated_data['field']).duration
        
        qs = Match.objects.filter(field=validated_data['field']).filter(date=validated_data['date'])
        for match in qs:
            final = (
                (dt.datetime.combine(dt.date(1,1,1),match.time) + 
                dt.timedelta(minutes=duration)).time()
            )
            if match.time <= validated_data['time'] <= final:
                raise serializers.ValidationError("Ese horario en la cancha seleccionada ya esta ocupado, selecciona otro horario!")

        validated_data['organizer'] = self.context['request'].user

        match = Match.objects.create(**validated_data)
        match.save()
        team_a = Team.objects.create(name=f'{match.id}_{match.date}_{match.time}_a')
        team_a.save()
        team_b = Team.objects.create(name=f'{match.id}_{match.date}_{match.time}_b')
        team_b.save()
        match.team.add(team_a, team_b)
        return match    

    # ?Match internal view and actions
class UserPlayerModelSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(source='id')
    class Meta:
        model = User 
        fields = ['user_id','username','first_name','last_name','email']

    # ?Match Organized - Player
class UserOrganizedMatchesModelSerializer(serializers.ModelSerializer):
    field = FieldSelectedListModelSerializer()

    class Meta:
        model = Match
        fields = ['id','field','date','time','category','active','date_created']

class PlayerRetriveModelSerializer(serializers.ModelSerializer):
    player_id = serializers.CharField(source='id')
    user_data = UserPlayerModelSerializer(source='user', read_only=True)
    position = serializers.CharField()
    photo = serializers.ImageField(use_url=True, read_only=True)
    class Meta:
        model = Player  
        fields = ['player_id','gender','position','photo','user_data']

class TeamPlayerModelSerializer(serializers.ModelSerializer):
    players = PlayerRetriveModelSerializer(many=True)
    class Meta:
        model = Team
        fields = ['id','name','players']

class MatchTeamPlayerModelSerializer(serializers.ModelSerializer):
    team = TeamPlayerModelSerializer(many=True)
    field = FieldRetriveModelSerializer()
    class Meta:
        model = Match
        fields = ['id','field','date','time','category','team','active']

    def update(self, instance, validated_data):

        if instance.active == False:
            raise serializers.ValidationError('Este partido no esta activo, intenta otro partido')

        player = Player.objects.get(user=self.context['request'].user.id)
        name = validated_data['team'][0].get('name')
        team = Team.objects.get(name=name)

        if player in team.players.all():
            team.players.remove(player)
        else:
            team.players.add(player)
            team.save()
        return instance
