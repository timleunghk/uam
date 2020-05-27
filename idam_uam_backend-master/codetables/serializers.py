import logging
from rest_framework import serializers
from .models import (
    Section, AdGroup, LnGroup, MasterRank, ActiveDirectoryOU, LnAccountType, LnClientLicense,
    LnMPSRange, LnMailFileOwner, LnMailServer, LnMailSystem, LnMailTemplate, LnLicenseType,
    LnAddressDomain, DpEmployeeType, DpRankCode, DpStaffGroup
)
# from common import utils
# from rest_polymorphic.serializers import PolymorphicSerializer

# from uam_requests.utils import AbstractRequestSerializer

LOGGER = logging.Logger(__name__)

# class TitleSerializer(AbstractRequestSerializer):
#     class Meta:
#         model = Title
#         fields = '__all__'
#         extra_kwargs = {'display_name': {'required': True},'created_by': {'required': True},'created_date': {'required': True}}

# class AccountTypeSerializer(AbstractRequestSerializer):
#     class Meta:
#         model = AccountType
#         fields = '__all__'
#         extra_kwargs = {'display_name': {'required': True},'created_by': {'required': True},'created_date': {'required': True}}


class SectionSerializer(serializers.ModelSerializer):

    display_text = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ('id', 'code', 'description', 'display_text')
        read_only_fields = (
            'id', 'code', 'description', 'display_text'
        )

    def get_display_text(self, instance):
        return '%s: %s' % (instance.code, instance.description)

# class RankSerializer(AbstractRequestSerializer):
#     class Meta:
#         model = Rank
#         fields = '__all__'
#         extra_kwargs = {'display_name': {'required': True},'created_by': {'required': True},'created_date': {'required': True}}

# class AccountTypeSerializer(AbstractRequestSerializer):
    # class Meta:
    #     model = AccountType
    #     fields = '__all__'
    #     extra_kwargs = {'display_name': {'required': True},'created_by': {'required': True},'created_date': {'required': True}}


class AdGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdGroup
        fields = ('id', 'name')
        read_only_fields = ('id', 'name')


class LnGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = LnGroup
        fields = ('id', 'name')
        read_only_fields = ('id', 'name')


class MasterRankSerializer(serializers.ModelSerializer):
    display_text = serializers.SerializerMethodField()

    class Meta:
        model = MasterRank
        fields = ['id', 'value', 'description', 'display_text']

    def get_display_text(self, instance):
        return '%s: %s' % (instance.value, instance.description)


class ADOUSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActiveDirectoryOU
        fields = ('id', 'name', 'is_default')
        read_only_fields = ('id', 'name', 'is_default')


class LnAccountTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LnAccountType
        fields = ('id', 'name', 'is_default')
        read_only_fields = ('id', 'name', 'is_default')


class LnClientLicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = LnClientLicense
        fields = ('id', 'name', 'is_default')
        read_only_fields = ('id', 'name', 'is_default')


class LnMailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LnMailTemplate
        fields = ('id', 'name', 'is_default')
        read_only_fields = ('id', 'name', 'is_default')


class LnMPSRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LnMPSRange
        fields = ('id', 'name', 'is_default')
        read_only_fields = ('id', 'name', 'is_default')


class LnMailServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = LnMailServer
        fields = ('id', 'name', 'is_default')
        read_only_fields = ('id', 'name', 'is_default')


class LnMailSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LnMailSystem
        fields = ('id', 'name', 'is_default')
        read_only_fields = ('id', 'name', 'is_default')


class LnLicenseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LnLicenseType
        fields = ('id', 'name', 'is_default')
        read_only_fields = ('id', 'name', 'is_default')


class LnMailFileOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = LnMailFileOwner
        fields = ('id', 'name', 'is_default')
        read_only_fields = ('id', 'name', 'is_default')


class LnAddressDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = LnAddressDomain
        fields = ('id', 'name', 'is_default')
        read_only_fields = ('id', 'name', 'is_default')


class DpEmployeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DpEmployeeType
        fields = ('id', 'name', 'is_default')
        read_only_fields = ('id', 'name', 'is_default')


class DpRankCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DpRankCode
        fields = ('id', 'name', 'is_default')
        read_only_fields = ('id', 'name', 'is_default')


class DpStaffGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DpStaffGroup
        fields = ('id', 'name', 'is_default')
        read_only_fields = ('id', 'name', 'is_default')
