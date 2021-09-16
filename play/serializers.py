
from rest_framework import serializers
from django.db.models.aggregates import Count
import datetime as dt

from .models import AddressField, validate_media_size

# !Sendgrid
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# !Django-Countries
from django_countries.serializer_fields import CountryField

# !Models
from .models import (
    Field,
    FootballType,
    Player,
    Manager,
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
        fields = ['username','first_name','last_name','email','password']
        extra_kwargs = {'password':{'write_only' : True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        player = Player.objects.create(user=user)
        player.save()

        message = Mail(
            from_email='playtogether.app.mx@gmail.com',
            to_emails= validated_data['email'],
            subject='Bienvenido a la experiencia PlaytogetherAPP',
            html_content=f'<strong><h1>{validated_data["username"]} Bienvenido a Playtogether</h1></strong>')
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)
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
        qs = Match.objects.filter(team__players=obj).filter(accepted=True).order_by('date')
        result = MatchListModelSerializer(qs, many=True).data
        return result 

    def get_matches_count(self, obj):
        return Match.objects.filter(team__players=obj).filter(accepted=True).count()

    def get_fields_count(self, obj):
        return Match.objects.filter(team__players=obj).filter(accepted=True).aggregate(Count('field_id', distinct=True))['field_id__count']
    
    class Meta:
        model = Player
        fields= ['player_id','dominant_food','position','photo','matches','matches_count','fields_count'] 

class UserPlayerRetriveModelSerializer(serializers.ModelSerializer):
    players = PlayerModelSerializer()

    class Meta:
        model = User
        fields = ['username','first_name', 'last_name','date_joined','players']

    # ?User-Player Profile Update
class PlayerDataPartialUpdateModelSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(use_url=True, validators=[validate_media_size])
    gender = serializers.ChoiceField(choices=Player.GENDER)

    class Meta:
        model = Player
        fields = ['gender','position','photo']

class UserDataPartialUpdateModelSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = User
        fields = ['username','first_name','last_name', 'email']

class UserPlayerPartialUpdateModelSerializer(serializers.ModelSerializer):
    user_data = UserDataPartialUpdateModelSerializer(source='*')
    player_data = PlayerDataPartialUpdateModelSerializer(source='players')

    class Meta:
        model = User
        fields = ['user_data','player_data']

    def update(self, instance, validated_data):
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

    # ?User Friends-Teammates
class PlayerTeammatesList(serializers.ModelSerializer):
    total_followers = serializers.SerializerMethodField()
    total_followings= serializers.SerializerMethodField()

    def get_total_followers(self, obj):
        player =  obj.players
        return player.friends.all().count()
    
    def get_total_followings(self, obj):
        player =  obj.players
        return player.teammates.all().count()
            
    class Meta:
        model = User 
        fields = ['total_followers','total_followings']

class PlayerTeammatesUpdateModelSerializer(serializers.ModelSerializer):
    response = serializers.SerializerMethodField()

    def get_response(self, obj):
        return 'Update Success'
    class Meta:
        model = User
        fields = ['response']

    def update(self, instance, validated_data):
        logged_user = self.context['request'].user.players
        player_to = instance.players
        
        if player_to.friends.filter(pk=logged_user.pk).exists():
            player_to.friends.remove(logged_user)
        else:
            player_to.friends.add(logged_user)

        return instance

# !Field
class FootballTypeRetriveModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FootballType
        fields = '__all__'

class FieldRetriveMatchListModelSerializer(serializers.ModelSerializer):
    address = serializers.CharField()
    football_type = FootballTypeRetriveModelSerializer()
    services = serializers.StringRelatedField(many=True, source='fields_services',read_only=True)
    matches = serializers.SerializerMethodField()

    def get_matches(self, obj):
        qs = Match.objects.filter(field=obj.id).filter(organizer__isnull=True)
        return MatchListModelSerializer(qs, many=True).data

    class Meta:
        model = Field
        fields = ['id','name','rent_cost','address','football_type','services','matches']

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
        fields = ['id','name','football_type']
    
class OrganizerRetriveModelSerializer(serializers.ModelSerializer):
    fields_count = serializers.SerializerMethodField()
    matches_count = serializers.SerializerMethodField()

    def get_matches_count(self, obj):
        return Match.objects.filter(team__players=obj.players).count()

    def get_fields_count(self, obj):
        return Match.objects.filter(team__players=obj.players).aggregate(Count('field_id', distinct=True))['field_id__count']
    
    class Meta:
        model = User
        fields = ['id','date_joined','username', 'fields_count', 'matches_count']

class MatchListModelSerializer(serializers.ModelSerializer):
    field = FieldSelectedListModelSerializer()
    date = serializers.DateField(required=True, input_formats=["%d-%m-%Y"])
    time = serializers.TimeField(required=True, input_formats=['%H:%M'])
    organizer =OrganizerRetriveModelSerializer()
    places_available= serializers.SerializerMethodField()

    def get_places_available(self, obj):
        result = None
        if obj.field.football_type:
            registered =  Match.objects.filter(id=obj.id).aggregate(registered=Count('team__players'))['registered']
            max_player = obj.field.football_type.max_players
            result = max_player - registered
        return result

    class Meta:
        model = Match
        fields = ['id','field','date','time','category','places_available', 'active','organizer', 'accepted']

    # ?Match internal view and actions
class UserPlayerModelSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(source='id')
    class Meta:
        model = User 
        fields = ['user_id','username','first_name','last_name','email']

    # ?Match Organized - Player
class UserOrganizedMatchesModelSerializer(serializers.ModelSerializer):
    field = FieldSelectedListModelSerializer()
    places_available= serializers.SerializerMethodField()

    def get_places_available(self, obj):
        result = None
        if obj.field.football_type:
            registered =  Match.objects.filter(id=obj.id).aggregate(registered=Count('team__players'))['registered']
            max_player = obj.field.football_type.max_players
            result = max_player - registered
        return result

    class Meta:
        model = Match
        fields = ['id','field','date','time','category','active','date_created','accepted', 'places_available']

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
        fields = ['id','date','time','category','organizer','field','team','active','accepted']

    def update(self, instance, validated_data):

        if instance.active == False:
                raise serializers.ValidationError('Este partido no esta activo, intenta otro')

        player = Player.objects.get(user=self.context['request'].user.id)
        name = validated_data['team'][0].get('name')
        team = Team.objects.get(name=name)

        if instance.category != 'mixto':
            if (
                instance.category == 'varonil' and player.gender != 'masculino' or 
                instance.category == 'femenil' and player.gender != 'femenino'
            ):
                raise serializers.ValidationError('No puedes unirte a esta categoria, intenta otro partido')

        if player in team.players.all():
            team.players.remove(player)
        else:
            team.players.add(player)
            team.save()
        return instance

    # ?Update Accepted-Delete-organizer-category
class MatchUpdateModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['organizer','accepted','category']
    
    def update(self, instance, validated_data):
        mails = [instance.field.managers.user.email]
        print(mails)
        if instance.organizer:
            mails += instance.organizer.email 

        message = Mail(
            from_email='playtogether.app.mx@gmail.com',
            to_emails= mails,
            subject='Revisa tus partidos',
            html_content=f'<strong><h1>Tu partido cambio de estatus</h1></strong>')
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)

        return super().update(instance, validated_data)

# !User FieldManager
    # ?User Manager Creation
class FieldManagerCreateModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','first_name', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data, is_staff=True)
        address = AddressField.objects.create()
        address.save()
        field = Field.objects.create(address=address)
        manager = Manager.objects.create(user=user, field=field)
        manager.save()

        message = Mail(
            from_email='playtogether.app.mx@gmail.com',
            to_emails= validated_data['email'],
            subject='Bienvenido a la experiencia PlaytogetherAPP',
            html_content=f'<strong><h1>{validated_data["username"]} Bienvenido a Playtogether</h1></strong>')
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)

        return user

    # ? User FieldManager Profile 
class FieldAddressModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressField
        fields = ['city','town','street','street_number']

class FieldFieldManagerRetriveModelSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(use_url=True)
    match_history = serializers.SerializerMethodField(source='get_matches')
    total_match_history = serializers.SerializerMethodField()
    pending_matches = serializers.SerializerMethodField()
    address = FieldAddressModelSerializer()

    def get_total_match_history(self, obj):
        user = self.context['request'].user
        return Match.objects.filter(field__managers__user= user).filter(accepted=True).count()

    def get_match_history(self, obj):
        user = self.context['request'].user
        qs = Match.objects.filter(field__managers__user= user).filter(accepted=True).order_by('date', 'time')
        return MatchListModelSerializer(qs, many=True).data

    def get_pending_matches(self, obj):
        user = self.context['request'].user
        qs = Match.objects.filter(field__managers__user= user).filter(accepted=False).order_by('organizer', 'date', 'time')
        return MatchListModelSerializer(qs, many=True).data

    class Meta:
        model = Field 
        fields = [
                    'id',
                    'name',
                    'rent_cost',
                    'address',
                    'football_type',
                    'photo',
                    'fields_services',
                    'show',
                    'pending_matches',
                    'total_match_history',
                    'match_history'
                    ]

class FieldManagerRetriveModelSerializer(serializers.ModelSerializer):
    field = FieldFieldManagerRetriveModelSerializer()
    photo = serializers.ImageField(use_url=True)
    class Meta:
        model = Manager
        fields = ['photo','field']

class UserFieldManagerRetriveModelSerializer(serializers.ModelSerializer):
    managers = FieldManagerRetriveModelSerializer()
    class Meta:
        model = User 
        fields = ['username','first_name','date_joined','managers']

    # ?User-FieldManager Update Profile
class FieldServicesListModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class FieldPartialUpdateModelSerializer(serializers.ModelSerializer):
    address = FieldAddressModelSerializer()
    photo = serializers.ImageField(use_url=True, validators=[validate_media_size])
    class Meta:
        model = Field
        fields = ['photo','name','rent_cost','address','football_type','fields_services']

class FieldManagerFieldPhotoPartialUpdateModelSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(use_url=True, validators=[validate_media_size])
    field = FieldPartialUpdateModelSerializer()
    class Meta:
        model = Manager
        fields = ['photo','field']

class UserFieldManagerPartialUpdateModelSerializer(serializers.ModelSerializer):
    managers = FieldManagerFieldPhotoPartialUpdateModelSerializer()
    manager_name = serializers.CharField(source='first_name')
    class Meta:
        model = User
        fields = ['manager_name','managers']

    def update(self, instance, validated_data):
        user = self.context['request'].user.id
        if user != instance.id:
            raise serializers.ValidationError({"Fail":"Not your profile"})

        manager_validated = validated_data.pop('managers')
        field_validated = manager_validated.pop('field')
        address_validated = field_validated.pop('address')

        manager = instance.managers
        field = manager.field
        address = field.address

        instance.first_name = validated_data.get('first_name', instance.first_name)
        manager.photo = manager_validated.get('photo', manager.photo)
        field.photo = field_validated.get('photo', field.photo)
        field.name = field_validated.get('name', field.name)
        field.rent_cost = field_validated.get('rent_cost', field.rent_cost)
        field.football_type = field_validated.get('football_type','field.football_type')
        address.city = address_validated.get('city', address.city)
        address.town = address_validated.get('town', address.town)
        address.street = address_validated.get('street', address.street)
        address.street_number = address_validated.get('street_number', address.street_number)

        if field.fields_services and field_validated.get('fields_services') != None:
            for fs in field.fields_services.all():
                field.fields_services.remove(fs)
            for fs in field_validated.get('fields_services'):
                field.fields_services.add(fs)
      
        instance.save()
        manager.save()
        field.save()
        address.save()
        return instance

    # ?Update Field "show" in Field
class UpdateShowFieldModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = ['show']

    def update(self, instance, validated_data):

        if (
            instance.football_type == None or
            instance.name == None or 
            instance.rent_cost == None
        ):
            instance.show = False
            raise serializers.ValidationError("Agrega: nombre, costo de renta y tipo de futbol a tu cancha para poder mostrarla")
        else:
            return super().update(instance, validated_data)

    # ?Create Matches as manager
class MatchCreationManagerModelSerializer(serializers.ModelSerializer):
    date = serializers.DateField(required=True, input_formats=["%d-%m-%Y"])
    time = serializers.TimeField(required=True, input_formats=['%H:%M'])

    class Meta:
        model = Match
        fields = ['id','field','date','time']

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

        match = Match.objects.create(**validated_data)
        match.save()
        team_a = Team.objects.create(name=f'{match.id}_{match.date}_{match.time}_a')
        team_a.save()
        team_b = Team.objects.create(name=f'{match.id}_{match.date}_{match.time}_b')
        team_b.save()
        match.team.add(team_a, team_b)
        return match    
