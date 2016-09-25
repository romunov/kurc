from django.db import models
from django.contrib.auth.models import User
from frontend.misc_functions import validate_file_extension
from oauth2client.contrib.django_orm import CredentialsField
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver


class Recipients(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=80)
    active = models.BooleanField()

    class Meta:
        verbose_name = "Recipient"
        verbose_name_plural = "Recipients"


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

    class Meta:
        verbose_name = 'Uploaded document'
        verbose_name_plural = 'Uploaded documents'

    def __str__(self):
        return self.docname


@receiver(post_delete, sender=UploadedDocs)
def delete_document(sender, instance, **kwargs):
    instance.docfile.delete(False)


class UserCredentials(models.Model):
    id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    credentials = CredentialsField()
