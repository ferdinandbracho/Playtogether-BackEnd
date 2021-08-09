from django.contrib.auth.models import User
from django.db import models
from django.db.models.base import Model
from django.db.models.deletion import CASCADE, PROTECT
from django_countries.fields import CountryField


# !Player
class  positions    (models.Model):
    position_name = models.CharField(max_length=50)

    def __str__(self):
        return self.position_name

class players(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name='user')
    GENDER = (
        ('femenino','Femenino'),
        ('masculino', 'Masculino')
    )
    gender = models.CharField(max_length=50, choices=GENDER, default='masculino', blank=True) 
    nationality = CountryField()
    position = models.ForeignKey(to=positions, on_delete=CASCADE, related_name='position', blank=True)
    FOOT = (
        ('derecho', 'Derecho'),
        ('izquierdo', 'Izquierdo')
    )
    dominant_food = models.CharField(max_length=50, choices=FOOT, default='derecho', blank=True)
    photo = models.ImageField(blank=True)

    def __str__(self) -> str:
        return self.user.first_name

# !Field
class addresses_fields(models.Model):
    city = models.CharField(max_length=50)
    town = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    street_number = models.CharField(max_length=10)

    def __str__(self) -> str:
        return f'Calle: {self.street} - Exterior: {self.street_number}'

class football_types(models.Model):
    name = models.CharField(max_length=50)
    max_players = models.IntegerField()
    min_players = models.IntegerField()

    def __str__(self) -> str:
        return self.name

class service(models.Model):
    service = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.service

class fields(models.Model):
    name = models.CharField(max_length=50)
    rent_cost = models.FloatField()
    address = models.OneToOneField(to=addresses_fields, on_delete=CASCADE, related_name='address')
    football_type = models.ForeignKey(to=football_types, on_delete=models.CASCADE, related_name='football_type')
    photo = models.ImageField()
    fields_services = models.ManyToManyField(to=service, related_name='fields_services')

    def __str__(self):
        return self.name
    
# !matches teams 
class teams(models.Model):
    name = models.CharField(max_length=50)
    match = models.ForeignKey(to='matches',on_delete=CASCADE ,related_name='match')
    players = models.ManyToManyField(to=players, related_name='players')

    def __str__(self):
        return self.name
    
class matches(models.Model):
    field = models.ForeignKey(to=fields, on_delete=PROTECT, related_name='field')
    date = models.DateField(auto_now=False, auto_now_add=False)
    time = models.TimeField(auto_now=False, auto_now_add=False)
    CATEGORY = (
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
        ('mixto', 'Mixto')
    )
    category = models.CharField(max_length=30, choices=CATEGORY)
    active = models.BooleanField(default=True)
    teams_a = models.ForeignKey(to=teams, on_delete=PROTECT, related_name='team_a', blank=True, null=True)
    teams_b = models.ForeignKey(to=teams, on_delete=PROTECT, related_name='team_b', blank=True, null=True)

    def __str__(self):
        return f'Partido: {self.id} - Fecha:{self.date} - Hora:{self.time}'
    