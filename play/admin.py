from django.contrib import admin
from .models import (
    #! User - player
    Player,
    Position,

    #! field
    Field,
    Service,
    AddressField,
    FootballType,

    #! match
    Match,
    Team,

    #! User - Manager
    Manager,
) 

admin.site.register(Player)
admin.site.register(Position)
admin.site.register(Field)
admin.site.register(Service)
admin.site.register(AddressField)
admin.site.register(FootballType)
admin.site.register(Match)
admin.site.register(Team)
admin.site.register(Manager)

