from django.db import models

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.db.models import URLField
from django.db.models.signals import post_delete
from django.utils import timezone

import os


# Create your models here.

class Organization(models.Model):
    name = models.CharField(max_length=50, unique=True)
    url = URLField()

    def __str__(self):
        return self.name


class AddedUser(models.Model):
    CHOICES = (
        ('manager', 'manager'),
        ('user', 'user')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    permission = models.CharField(max_length=50, choices=CHOICES, default='user')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


def UploadPath(instance, filename):
    return '%s/%s' % (instance.organization.name, filename)


class Json(models.Model):
    archive = models.FileField(upload_to=UploadPath)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return os.path.basename(self.archive.name)
        
    def basename(self):
        return os.path.basename(self.archive.name)
        
    def extension(self):
        return os.path.splitext(self.archive.name)[1].replace(".", "").upper()
        
    def dirname(self):
        return 'media/' + os.path.dirname(self.archive.name) + '/' + os.path.basename(self.archive.name)
        
    def datetime(self):
        return self.update_time.strftime('%Y-%m-%d %H:%M:%S')


class Image(models.Model):
    archive = models.ImageField(upload_to=UploadPath)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return os.path.basename(self.archive.name)
        
    def basename(self):
        return os.path.basename(self.archive.name)
        
    def extension(self):
        return os.path.splitext(self.archive.name)[1].replace(".", "").upper()
        
    def dirname(self):
        return 'media/' + os.path.dirname(self.archive.name) + '/' + os.path.basename(self.archive.name)
        
    def datetime(self):
        return self.update_time.strftime('%Y-%m-%d %H:%M:%S')


class Thumbnail(models.Model):
    archive = models.ImageField(upload_to=UploadPath)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return os.path.basename(self.archive.name)
        
    def dirname(self):
        return 'media/' + os.path.dirname(self.archive.name) + '/' + os.path.basename(self.archive.name)


class Bin(models.Model):
    archive = models.FileField(upload_to=UploadPath)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    thumbnail = models.ForeignKey(Thumbnail, on_delete=models.CASCADE)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return os.path.basename(self.archive.name)
        
    def basename(self):
        return os.path.basename(self.archive.name)
        
    def extension(self):
        return os.path.splitext(self.archive.name)[1].replace(".", "").upper()
        
    def dirname(self):
        return 'media/' + os.path.dirname(self.archive.name) + '/' + os.path.basename(self.archive.name)
        
    def datetime(self):
        return self.update_time.strftime('%Y-%m-%d %H:%M:%S')


@receiver(post_delete, sender=Json)
@receiver(post_delete, sender=Image)
@receiver(post_delete, sender=Thumbnail)
@receiver(post_delete, sender=Bin)
def submission_delete(sender, instance, **kwargs):
    instance.archive.delete(False)


class ImageBin(models.Model):
    image = models.OneToOneField(Image, on_delete=models.CASCADE, null=True)
    bin = models.OneToOneField(Bin, on_delete=models.CASCADE, null=True)


class Tag(models.Model):
    mac = models.CharField(max_length=17, unique=True)
    name = models.CharField(max_length=50, blank=True)
    level = models.IntegerField(default=0)
    owner = models.CharField(max_length=50, blank=True)
    power = models.CharField(max_length=50, blank=True)
    mcuver = models.CharField(max_length=50, blank=True)
    wifiver = models.CharField(max_length=50, blank=True)
    tconver = models.CharField(max_length=50, blank=True)
    content_type = models.ForeignKey(ContentType, blank=True, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    tag_file = GenericForeignKey('content_type', 'object_id')
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.mac


class TagOrg(models.Model):
    tag = models.OneToOneField(Tag, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.tag.mac
    

"""
class UploadFile(models.Model):
    upload_file = models.FileField(upload_to=upload)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return os.path.basename(self.upload_file.name)
"""
