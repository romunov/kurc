from django.db import models
from django.contrib.auth.models import User
from frontend.misc_functions import validate_file_extension


class Recipients(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=80)


class PostNameNum(models.Model):
    id = models.AutoField(primary_key=True)
    post_number = models.IntegerField()
    post_name = models.CharField(max_length=80)
    country = models.CharField(max_length=10)


class UserAddress(models.Model):
    id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    street = models.CharField(max_length=80, default="", blank=True)
    post_name = models.CharField(max_length=80, default="", blank=True)
    post_number = models.IntegerField(default=None, blank=True, null=True)


class Docs(models.Model):
    id = models.AutoField(primary_key=True)
    docname = models.CharField(max_length=50)
    doccount = models.IntegerField(default=0)
    active = models.BooleanField()

    class Meta:
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'

    # Added this because it changes how entries are displayed in the Admin site.
    def __str__(self):
        return self.docname


class Activity(models.Model):
    id = models.AutoField(primary_key=True)
    docid = models.ForeignKey(Docs, on_delete=models.CASCADE)
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    sentto = models.ForeignKey(Recipients, on_delete=models.CASCADE)
    datumtime = models.DateTimeField()


class UploadedDocs(models.Model):
    id = models.AutoField(primary_key=True)
    docname = models.CharField(max_length=50)
    docfile = models.FileField(validators=[validate_file_extension])
    docuser = models.ForeignKey(User, on_delete=models.CASCADE)
    doctime = models.DateTimeField(auto_now_add=True, blank=True)
