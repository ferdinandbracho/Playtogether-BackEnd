from django.contrib.auth.models import User
from django.db import models
from django.db.models.deletion import CASCADE
from django_countries.fields import CountryField
import datetime as dt
from django.core.exceptions import ValidationError

def media_path(instance, filename):
    return 'user_{0}/avatar'.format(instance.user.id)

def media_path_field(instance, filename):
    return 'field_{0}/img'.format(instance.id)  
 

def validate_media_size(value):
    media_size = value.size
    if media_size > 1048562:
        raise ValidationError('El tamano maximo de la imagen a cargar es de 1MB')
    else:
        return value

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
    gender = models.CharField(max_length=50, choices=GENDER, blank=True) 
    nationality = CountryField(blank=True, null=True)
    position = models.ForeignKey(to=Position,on_delete=CASCADE, related_name='players', blank=True, null=True)
    position = models.ForeignKey(to=Position,on_delete=CASCADE, related_name='players', blank=True, null=True)
    FOOT = (
        ('derecho', 'Derecho'),
        ('izquierdo', 'Izquierdo')
    )
    dominant_food = models.CharField(max_length=50, choices=FOOT, blank=True)
    photo = models.ImageField(blank=True, upload_to=media_path,default='avatar_default.png', validators=[validate_media_size])

    def __str__(self):
        return self.user.first_name 

# !Field
class AddressField(models.Model):
    city = models.CharField(max_length=50, blank=True)
    town = models.CharField(max_length=50, blank=True)
    street = models.CharField(max_length=50, blank=True)
    street_number = models.CharField(max_length=10, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.street_number} {self.street} {self.town}'

class FootballType(models.Model):
    name = models.CharField(max_length=50)
    duration = models.IntegerField()
    max_players = models.IntegerField()
    min_players = models.IntegerField()

    def __str__(self) -> str:
        return self.name

class Service(models.Model):
    service = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.service

class Field(models.Model):
    name = models.CharField(max_length=50,blank=True)
    rent_cost = models.FloatField(blank=True, null=True)
    address = models.OneToOneField(to=AddressField, on_delete=CASCADE, blank=True, null=True,related_name='fields')
    football_type = models.ForeignKey(to=FootballType, on_delete=models.CASCADE, blank=True, null=True, related_name='fields')
    photo = models.ImageField(blank=True, upload_to=media_path_field, default='default_field.png')
    fields_services = models.ManyToManyField(to=Service, blank=True, related_name='fields')
    show = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
# !matches teams 
class Match(models.Model):
    field = models.ForeignKey(to=Field, on_delete=CASCADE, related_name='matches')
    date = models.DateField(auto_now=False, auto_now_add=False)
    time = models.TimeField(auto_now=False, auto_now_add=False)
    CATEGORY = (
        ('varonil', 'Varonil'),
        ('femenil', 'Femenil'),
        ('mixto', 'Mixto')
    )
    category = models.CharField(max_length=30, choices=CATEGORY)
    active = models.BooleanField(default=True)
    team = models.ManyToManyField(to='Team',related_name='matches')
    organizer = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='matches',blank=True, null=True)
    accepted = models.BooleanField(default=False, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Partido: {self.id} - Fecha:{self.date} - Hora:{self.time}'

    def datetime_checker(self):
        now = dt.datetime.today()

        if (
                self.date < now.date() or
                self.date == now.date() and 
                self.time < now.time()
            ):
            self.active = False
            self.save()
        else:            
            self.active = True
            self.save()
        return self
    
class Team(models.Model):
    name = models.CharField(max_length=50)
    players = models.ManyToManyField(to=Player, related_name='teams', blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# !manager 
class Manager(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name='managers')
    field = models.OneToOneField(to='Field', on_delete=models.CASCADE, related_name='managers')
    photo = models.ImageField(blank=True, upload_to=media_path ,default='manager_default.png', validators=[validate_media_size])
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.first_name