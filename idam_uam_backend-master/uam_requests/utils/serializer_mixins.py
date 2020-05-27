from rest_framework import serializers
from uam_requests import models
from uam_users.models import UamUser
from codetables.models import (
    AdGroup, LnGroup, LnClientLicense, LnAccountType, ActiveDirectoryOU,
    LnMPSRange, LnMailFileOwner, LnMailServer, LnMailSystem, LnMailTemplate, LnLicenseType,
    LnAddressDomain, DpEmployeeType, DpRankCode, DpStaffGroup,
)
from uam_users.serializers import UamUserSerializer
from codetables.serializers import (AdGroupSerializer, LnGroupSerializer, MasterRankSerializer, ADOUSerializer,
                                    LnAccountTypeSerializer)
from common import utils


class DetermineReadOnlyMix(serializers.ModelSerializer):
    '''
    A serializer Mixin for determining if current instance is for read-only.  This mixin will add a field read_only with boolean type to current serializer.
    Subclass shall implement _get_if_readonly to return if the current instance is for read-only.  Frontend program shall read the read_only field to decide whether
    to show enquiry view or edit view
    '''
    read_only = serializers.SerializerMethodField()

    def _get_if_readonly(self, _instance, _user):
        '''
        Subclass shall return True if user should not update current record, else False
        '''
        raise Exception(
            'Subclass shall implement this method to return if the instance if readonly to current user or not')

    def get_read_only(self, instance):
        request = self.context.get('request', None)
        if request and request.user:
            return self._get_if_readonly(instance, request.user)
        else:
            return True


class MailToSerializerMixin(serializers.Serializer):
    mail_to = serializers.SerializerMethodField()
    update_mail_to = serializers.JSONField(write_only=True, required=False)
    class RequestMailToSerializer(serializers.ModelSerializer):

        class Meta:
            model = models.RequestMailTo
            fields = ('id', 'to', 'status', 'cc')
            read_only_fields = ('status',)

    def _get_current_mail_status(self):
        '''
        Subclass shall return the corresponding status for current mail to be sent (e.g. BaseRequest.STATUS_NEW for preparing CreateAccountRequest for submission)
        '''
        raise Exception(
            'Subclass shall implement this method to return expected status of mail record to be created')

    def get_mail_to(self, value):
        try:
            mail_to = models.RequestMailTo.objects.get(
                request=value, status=self._get_current_mail_status())
        except models.RequestMailTo.DoesNotExist:
            mail_to = models.RequestMailTo(
                status=self._get_current_mail_status())
        serializer = self.RequestMailToSerializer(instance=mail_to)
        return serializer.data

    def _pre_save(self, validated_data, updated_instance):
        pre_save_dict = super()._pre_save(validated_data, updated_instance)
        pre_save_dict.update(
            {'update_mail_to': validated_data.pop('update_mail_to', None)})
        return pre_save_dict

    def _post_save(self, validated_data, updated_instance, pre_save_dict):
        updated_instance = super()._post_save(
            validated_data, updated_instance, pre_save_dict)
        tmp_mail_to = pre_save_dict.get('update_mail_to', None)
        if tmp_mail_to:
            tmp_mail_to_id = tmp_mail_to.pop('id', None)
            tmp_mail_to['status'] = self._get_current_mail_status()
            _result, _created = models.RequestMailTo.objects.update_or_create(
                id=tmp_mail_to_id, defaults=tmp_mail_to, request=updated_instance)
        return updated_instance

    # def _save_instance(self, updated_instance, validated_data):
    #     tmp_mail_to = validated_data.pop('update_mail_to', None)
    #     req = super(MailToSerializerMixin, self)._save_instance(updated_instance, validated_data)
    #     if tmp_mail_to:
    #         tmp_mail_to_id = tmp_mail_to.pop('id', None)
    #         tmp_mail_to['status'] = self._get_current_mail_status()
    #         result, created = models.RequestMailTo.objects.update_or_create(id=tmp_mail_to_id, defaults=tmp_mail_to, request=req)
    #     return req


class RequestUploadFileMixin(serializers.Serializer):
    uploaded_files = serializers.SerializerMethodField()
    delete_files = serializers.JSONField(write_only=True, required=False)

    def get_uploaded_files(self, value):
        uploaded_files = models.RequestFile.objects.filter(request=value)
        rtn_arr = {}
        for file in uploaded_files:
            if file.status not in rtn_arr:
                rtn_arr[file.status] = []
            rtn_arr[file.status].append(
                {'id': file.id, 'file_name': file.file_name, 'url': file.file.url, 'size': file.file.size})
        return rtn_arr

    def _pre_save(self, validated_data, updated_instance):
        pre_save_dict = super()._pre_save(validated_data, updated_instance)
        pre_save_dict.update(
            {'delete_files': validated_data.pop('delete_files', None)})
        return pre_save_dict

    def _post_save(self, validated_data, updated_instance, pre_save_dict):
        updated_instance = super()._post_save(
            validated_data, updated_instance, pre_save_dict)
        delete_files = pre_save_dict.get('delete_files', None)
        if delete_files:
            _result = models.RequestFile.objects.filter(
                pk__in=delete_files, request=updated_instance).delete()
        return updated_instance

    # def _save_instance(self, updated_instance, validated_data):
    #     delete_files = validated_data.pop('delete_files', None)
    #     req = super()._save_instance(updated_instance, validated_data)
    #     if delete_files and len(delete_files) > 0:
    #         result = models.RequestFile.objects.filter(pk__in=delete_files, request=req).delete()
    #     return req


class LnAdGroupRelatedMixin(serializers.Serializer):
    ad_user_groups = AdGroupSerializer(many=True, read_only=True)
    update_ad_user_groups = serializers.JSONField(
        write_only=True, required=False)
    ln_user_groups = LnGroupSerializer(many=True, read_only=True)
    update_ln_user_groups = serializers.JSONField(
        write_only=True, required=False)

    def _pre_save(self, validated_data, updated_instance):
        pre_save_dict = super()._pre_save(validated_data, updated_instance)
        pre_save_dict.update(
            {'update_ad_user_groups': validated_data.pop('update_ad_user_groups', None)})
        pre_save_dict.update(
            {'update_ln_user_groups': validated_data.pop('update_ln_user_groups', None)})
        return pre_save_dict

    def _post_save(self, validated_data, updated_instance, pre_save_dict):
        updated_instance = super()._post_save(
            validated_data, updated_instance, pre_save_dict)
        update_ad_user_groups = pre_save_dict.get(
            'update_ad_user_groups', None)
        if update_ad_user_groups is not None and isinstance(update_ad_user_groups, list):
            ids = [group.get('id', -1) for group in update_ad_user_groups]
            final_groups = AdGroup.objects.filter(pk__in=ids)
            updated_instance.ad_user_groups.set(final_groups)
            # result = models.RequestFile.objects.filter(pk__in=delete_files, request=updated_instance).delete()
        update_ln_user_groups = pre_save_dict.get(
            'update_ln_user_groups', None)
        if update_ln_user_groups is not None and isinstance(update_ln_user_groups, list):
            ids = [group.get('id', -1) for group in update_ln_user_groups]
            final_groups = LnGroup.objects.filter(pk__in=ids)
            updated_instance.ln_user_groups.set(final_groups)
        return updated_instance


class RelatedUserInfoMixin(serializers.Serializer):
    original_user_info = serializers.SerializerMethodField()

    def get_original_user_info(self, value):
        related_user: UamUser = getattr(value, 'related_user', None)
        if related_user:
            return {
                'oa_need_windows_login': related_user.oa_need_windows_login,
                'oa_need_dp': related_user.oa_need_dp,
                'oa_need_jjo': related_user.oa_need_jjo,
                'oa_need_lotus_notes': related_user.oa_need_lotus_notes,
            }
        else:
            return None


class ForeignKeyPersonalInfoMixin(serializers.Serializer):
    updated_section = serializers.JSONField(
        write_only=True, required=False, allow_null=True)
    master_rank = MasterRankSerializer(many=False, read_only=True)
    updated_master_rank = serializers.JSONField(
        write_only=True, required=False, allow_null=True)
    substantive_rank = MasterRankSerializer(many=False, read_only=True)
    updated_substantive_rank = serializers.JSONField(
        write_only=True, required=False, allow_null=True)
    ad_ou = serializers.PrimaryKeyRelatedField(
        many=False, queryset=ActiveDirectoryOU.objects.all(), required=False, allow_null=True)
    ad_ps_magistrate_of_lt = serializers.JSONField(
        required=False, allow_null=True)
    ln_account_type = serializers.PrimaryKeyRelatedField(
        many=False, queryset=LnAccountType.objects.all(), required=False, allow_null=True)
    ln_client_license = serializers.PrimaryKeyRelatedField(
        many=False, queryset=LnClientLicense.objects.all(), required=False, allow_null=True)
    ln_mps_range = serializers.PrimaryKeyRelatedField(
        many=False, queryset=LnMPSRange.objects.all(), required=False, allow_null=True)
    ln_mail_system = serializers.PrimaryKeyRelatedField(
        many=False, queryset=LnMailSystem.objects.all(), required=False, allow_null=True)
    ln_mail_file_owner = serializers.PrimaryKeyRelatedField(
        many=False, queryset=LnMailFileOwner.objects.all(), required=False, allow_null=True)
    ln_mail_template = serializers.PrimaryKeyRelatedField(
        many=False, queryset=LnMailTemplate.objects.all(), required=False, allow_null=True)
    ln_mail_server = serializers.PrimaryKeyRelatedField(
        many=False, queryset=LnMailServer.objects.all(), required=False, allow_null=True)
    ln_license_type = serializers.PrimaryKeyRelatedField(
        many=False, queryset=LnLicenseType.objects.all(), required=False, allow_null=True)
    ln_mail_domain = serializers.PrimaryKeyRelatedField(
        many=False, queryset=LnAddressDomain.objects.all(), required=False, allow_null=True)
    jjo_mail_domain = serializers.PrimaryKeyRelatedField(
        many=False, queryset=LnAddressDomain.objects.all(), required=False, allow_null=True)
    dp_emp_type = serializers.PrimaryKeyRelatedField(
        many=False, queryset=DpEmployeeType.objects.all(), required=False, allow_null=True)
    dp_rank_code = serializers.PrimaryKeyRelatedField(
        many=False, queryset=DpRankCode.objects.all(), required=False, allow_null=True)
    dp_staff_code = serializers.PrimaryKeyRelatedField(
        many=False, queryset=DpStaffGroup.objects.all(), required=False, allow_null=True)
    jjo_emp_type = serializers.PrimaryKeyRelatedField(
        many=False, queryset=DpEmployeeType.objects.all(), required=False, allow_null=True)

    def _rename_updated_foreign_field(self, fieldname, validated_data, id_field='id'):
        update_fieldname = 'updated_%s' % fieldname
        fieldname_id = '%s_id' % fieldname
        tmp_obj = validated_data.pop(update_fieldname, None)
        if tmp_obj and id_field in tmp_obj:
            validated_data.update(
                {fieldname_id: tmp_obj[id_field]}
            )
        else:
            validated_data.update(
                {fieldname_id: None}
            )

    def _pre_save(self, validated_data, updated_instance):
        pre_save_dict = super()._pre_save(validated_data, updated_instance)
        self._rename_updated_foreign_field('master_rank', validated_data)
        self._rename_updated_foreign_field('substantive_rank', validated_data)
        self._rename_updated_foreign_field(
            'section', validated_data, id_field='code')
        return pre_save_dict


class DisableConcurrentCheckMixin:
    '''
    Request serializer inheriting from this method will have optimistic lock disabled
    '''
    pass


class AccountInfoSerializerMixin(serializers.Serializer):

    def to_representation(self, obj):
        to_return = super().to_representation(obj)
        if hasattr(obj, 'related_user'):
            serializer = UamUserSerializer(instance=obj.related_user)
            tmp_return = serializer.data
            tmp_return.update(to_return)
            to_return = tmp_return
        return to_return
