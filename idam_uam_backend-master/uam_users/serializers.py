from rest_framework import serializers
# from common.utils import DATE_FORMAT, DATETIME_FORMAT, DateTimeFieldWithTZ
from common.utils import DateTimeFieldWithTZ
from codetables.serializers import (AdGroupSerializer, LnGroupSerializer,
                                    MasterRankSerializer, SectionSerializer, )
from .models import UamUser


class UamUserSerializer(serializers.ModelSerializer):
    # account_effective_start_date = serializers.DateField(format=DATE_FORMAT, input_formats=[DATE_FORMAT])
    # account_effective_end_date = serializers.DateField(format=DATE_FORMAT, input_formats=[DATE_FORMAT], required=False, allow_null=True)

    creation_date = DateTimeFieldWithTZ(read_only=True)
    last_modification_date = DateTimeFieldWithTZ(read_only=True)
    # submission_date = serializers.DateField(read_only=True)
    creation_user = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username',
    )
    last_modification_user = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username',
    )

    ad_user_groups = AdGroupSerializer(many=True, read_only=True)

    ln_user_groups = LnGroupSerializer(many=True, read_only=True)

    account_status_name = serializers.SerializerMethodField()

    master_rank = MasterRankSerializer(many=False, read_only=True)
    substantive_rank = MasterRankSerializer(many=False, read_only=True)
    section = SectionSerializer(many=False, read_only=True)
    # ad_ou = ADOUSerializer(many=False, read_only=True)
    # ln_account_type = LnAccountTypeSerializer(many=False, read_only=True)
    # ln_client_license = serializers.PrimaryKeyRelatedField(many=False, queryset=LnClientLicense.objects.all())
    ad_ou = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    ad_ps_magistrate_of_lt = serializers.JSONField(read_only=True)
    ln_account_type = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True)
    ln_client_license = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True)
    ln_mps_range = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True)
    ln_mail_system = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True)
    ln_mail_file_owner = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True)
    ln_mail_template = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True)
    ln_mail_server = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True)
    ln_license_type = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True)
    ln_mail_domain = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True)
    jjo_mail_domain = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True)
    jjo_emp_type = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True)
    dp_emp_type = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True)
    dp_rank_code = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True)
    dp_staff_code = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True)

    def get_account_status_name(self, value):
        return UamUser.ACCOUNT_STATUS[value.account_status][1]

    # def to_representation(self, obj):
    #     to_rep = super().to_representation(obj)
    #     account_status_code = to_rep['account_status']
    #     account_status_name = UamUser.ACCOUNT_STATUS[account_status_code][1]
    #     to_rep.update({'account_status_name': account_status_name})
        # if hasattr(obj, 'creation_date') and obj.creation_date is not None:
        #     to_rep.update({'creation_date': obj.creation_date.strftime("%d/%m/%Y %H:%M:%S")})
        # if hasattr(obj, 'last_modification_date') and obj.last_modification_date is not None:
        #     to_rep.update({'last_modification_date': obj.last_modification_date.strftime("%d/%m/%Y %H:%M:%S")})
        # return to_rep

    class Meta:
        model = UamUser
        # fields = '__all__'
        read_only_fields = ('ad_sync_time', 'notes_sync_time', 'uam_id',)
        exclude = ('_ad_ps_magistrate_of_lt',)


class UamUserListSerializer(serializers.ModelSerializer):
    section = serializers.SerializerMethodField()
    account_status_name = serializers.SerializerMethodField()

    class Meta:
        model = UamUser
        fields = (
            'id', 'uam_id', 'surname', 'given_name', 'ad_windows_login_name', 'ln_lotus_notes_mail_name',
            'post_title', 'section', 'account_status_name', 'account_status',
        )

    def get_section(self, instance):
        return {'id': instance['section__id'], 'code': instance['section__code']}

    def get_account_status_name(self, instance):
        return instance['account_status_name']