from django.contrib import admin
from .models import (
    #player
    Player,
    Position,

    # field
    Field,
    Service,
    AddressField,
    FootballType,

    # match
    Match,
    Team,
) 

admin.site.register(Player)
admin.site.register(Position)
admin.site.register(Field)
admin.site.register(Service)
admin.site.register(AddressField)
admin.site.register(FootballType)
admin.site.register(Match)
admin.site.register(Team)

