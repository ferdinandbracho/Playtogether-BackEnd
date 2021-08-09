from django.contrib import admin
from .models import (
    #player
    players,
    positions,

    # field
    fields,
    service,
    addresses_fields,
    football_types,

    # match
    matches,
    teams,
) 

admin.site.register(players)
admin.site.register(positions)
admin.site.register(fields)
admin.site.register(service)
admin.site.register(addresses_fields)
admin.site.register(football_types)
admin.site.register(matches)
admin.site.register(teams)

