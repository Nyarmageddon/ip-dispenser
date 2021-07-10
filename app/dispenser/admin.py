from django.contrib import admin

from dispenser.models import IPAddress, IPSubnet

admin.site.register(IPSubnet)
admin.site.register(IPAddress)
