from django.db import models
from django.contrib.auth.models import User

class AbstractBaseModel(models.Model):
    ''' Base class for all models.  This model will automatically record creation and modification date '''
    class Meta:
        abstract = True
    
    creation_date = models.DateTimeField(auto_now_add=True)
    creation_user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name="%(app_label)s_%(class)s_created", related_query_name="%(app_label)s_%(class)ss")
    last_modification_date = models.DateTimeField(auto_now=True)
    last_modification_user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name="%(app_label)s_%(class)s_modified", related_query_name="%(app_label)s_%(class)ss")

    # def save(self, **kwargs):
    #     ''' Capture user information from request and put them into the field creation_user and last_modification_user according '''
    #     if ('request' in kwargs):
    #         saving_user = kwargs['request'].user
    #         if saving_user is not None:
    #             self.last_modification_user = saving_user
    #             if self.id is None:
    #                 self.creation_user = saving_user
    #     super(AbstractBaseModel, self).save(*args, **kwargs)