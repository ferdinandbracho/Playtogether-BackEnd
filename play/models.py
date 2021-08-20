from django.contrib.auth.models import User
from django.db import models
from django.db.models.deletion import CASCADE
from django_countries.fields import CountryField

def media_path(instance, filename):
    return 'user_{0}/avatar'.format(instance.user.id)

def media_path_field(instance, filename):
    return 'field_{0}/img'.format(instance.id)


# !Player
class  Position(models.Model):
    position_name = models.CharField(max_length=50)

    def __str__(self):
        return self.position_name

class Player(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name='players')
    GENDER = (
        ('femenino','Femenino'),
        ('masculino', 'Masculino')
    )
    gender = models.CharField(max_length=50, choices=GENDER, default='Masculino', blank=True) 
    nationality = CountryField()
    position = models.ForeignKey(to=Position, on_delete=CASCADE, related_name='players', blank=True)
    FOOT = (
        ('derecho', 'Derecho'),
        ('izquierdo', 'Izquierdo')
    )
    dominant_food = models.CharField(max_length=50, choices=FOOT, default='Derecho', blank=True)
    photo = models.ImageField(blank=True, upload_to=media_path,default='avatar_default.png')

    def __str__(self):
        return self.user.first_name
    

# !Field
class AddressField(models.Model):
    city = models.CharField(max_length=50)
    town = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    street_number = models.CharField(max_length=10)

    def __str__(self) -> str:
        return f'Delegacion: {self.town} - Calle: {self.street} - Exterior: {self.street_number}'

class FootballType(models.Model):
    name = models.CharField(max_length=50)
    max_players = models.IntegerField()
    min_players = models.IntegerField()

    def __str__(self) -> str:
        return self.name

class Service(models.Model):
    service = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.service

class Field(models.Model):
    name = models.CharField(max_length=50)
    rent_cost = models.FloatField()
    address = models.OneToOneField(to=AddressField, on_delete=CASCADE, related_name='fields')
    football_type = models.ForeignKey(to=FootballType, on_delete=models.CASCADE, related_name='fields')
    photo = models.ImageField(blank=True, upload_to=media_path_field, default='field_default.jpg')
    fields_services = models.ManyToManyField(to=Service, related_name='fields')

    def __str__(self):
        return self.name
    
# !matches teams 
class Match(models.Model):
    field = models.ForeignKey(to=Field, on_delete=CASCADE, related_name='matches')
    date = models.DateField(auto_now=False, auto_now_add=False)
    time = models.TimeField(auto_now=False, auto_now_add=False)
    CATEGORY = (
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
        ('mixto', 'Mixto')
    )
    category = models.CharField(max_length=30, choices=CATEGORY)
    active = models.BooleanField(default=True)
    team = models.ManyToManyField(to='Team',related_name='matches')

    def __str__(self):
        return f'Partido: {self.id} - Fecha:{self.date} - Hora:{self.time}'
    
class Team(models.Model):
    name = models.CharField(max_length=50)
    players = models.ManyToManyField(to=Player, related_name='teams')

    def __str__(self):
        return self.name
    