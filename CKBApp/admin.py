from django.contrib import admin
from .models import User, Student, Educator, Tournament, Team, Battle, Invite

admin.site.register(User)
admin.site.register(Student)
admin.site.register(Educator)
admin.site.register(Tournament)
admin.site.register(Team)
admin.site.register(Battle)
admin.site.register(Invite)
