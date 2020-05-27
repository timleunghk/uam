'''
Models for Code Tables
'''
from django.db import models
from common.models import AbstractBaseModel

# Create your models here.


class Title(models.Model):
    '''
    Title Model
    '''
    value = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return '%s - %s' % (self.id, self.value)


class MasterRank(AbstractBaseModel):
    '''
    Master Rank Model
    '''
    value = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return '%s - %s' % (self.id, self.value)


class AccountType(models.Model):
    '''
    Account Type Model
    '''

    value = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return '%s - %s' % (self.id, self.value)


class Section(AbstractBaseModel):
    '''
    Section Model
    '''

    code = models.SlugField(null=False, blank=False, unique=True)
    description = models.CharField(null=False, max_length=1000)

    def __str__(self):
        return '%s - %s - %s' % (self.id, self.code, self.description)


class AbstractSimpleCodeModel(AbstractBaseModel):

    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return '%s - %s - Active: %s - Is Default?: %s' % (self.id, self.name, self.active, self.is_default)

    class Meta:
        abstract = True


class AdGroup(AbstractSimpleCodeModel):
    '''
    AD Group Model
    '''
    pass


class LnGroup(AbstractSimpleCodeModel):
    '''
    Lotus Note Group Model
    '''
    pass


class SectionRelatedMixin(models.Model):
    '''
    A mixin for Model with reference to Section model (e.g. an UamUser belonging to a Section, A request belonging to a Section)
    '''
    class Meta:
        abstract = True

    section = models.ForeignKey(
        Section, on_delete=models.PROTECT, null=True, to_field='code')


class ActiveDirectoryOU(AbstractSimpleCodeModel):
    '''
    Valid AD OU
    '''
    pass


class LnAccountType(AbstractSimpleCodeModel):
    '''
    Valid Lotus Notes Account Type
    '''
    pass


class LnClientLicense(AbstractSimpleCodeModel):
    '''
    Valid Lotus Notes Account Type
    '''
    pass


class LnMPSRange(AbstractSimpleCodeModel):
    '''
    Valid Lotus Notes MPS Range
    '''
    pass


class LnMailSystem(AbstractSimpleCodeModel):
    '''
    Valid Lotus Notes Mail System
    '''
    pass


class LnMailServer(AbstractSimpleCodeModel):
    '''
    Valid Lotus Notes Mail Servers
    '''
    pass


class LnMailFileOwner(AbstractSimpleCodeModel):
    '''
    Valid Lotus Notes Mail file owner
    '''
    pass


class LnMailTemplate(AbstractSimpleCodeModel):
    '''
    Valid Lotus Notes Mail Template
    '''
    pass


class LnAddressDomain(AbstractSimpleCodeModel):
    '''
    Valid Lotus Notes Mail domain (e.g. @judiciary.hk, @cfa.hk)
    '''
    pass


class LnLicenseType(AbstractSimpleCodeModel):
    '''
    Valid Licnese Type (e.g. International, Web)
    '''
    pass

class DpRankCode(AbstractSimpleCodeModel):
    pass

class DpStaffGroup(AbstractSimpleCodeModel):
    pass

class DpEmployeeType(AbstractSimpleCodeModel):
    pass