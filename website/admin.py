from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Organization)
admin.site.register(models.AddedUser)
admin.site.register(models.Json)
admin.site.register(models.Image)
admin.site.register(models.Bin)
admin.site.register(models.ImageBin)
admin.site.register(models.Tag)
admin.site.register(models.TagOrg)
admin.site.register(models.Thumbnail)