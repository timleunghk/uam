from rest_framework import serializers
from uam_requests.utils import (
    ForeignKeyPersonalInfoMixin, LnAdGroupRelatedMixin, DetermineReadOnlyMix,
    RequestUploadFileMixin, MailToSerializerMixin, AbstractRequestSerializer, prevent_account_exist,
    convert_external_sync_for_remote, convert_accountrequest_send_mail, RelatedUserInfoMixin,
)
from uam_requests.models import UpdateAccountRequest
from common import utils
from codetables.serializers import SectionSerializer
from interface.models import ExternalSync
from uam_users.models import UamUser


class UpdateAccountRequestSerializer(RelatedUserInfoMixin, serializers.ModelSerializer):
    section = SectionSerializer(many=False, read_only=True)

    '''
    Generic Serializer for Update Account Request
    '''
    class Meta:
        model = UpdateAccountRequest
        fields = '__all__'


class UpdateAccountRequestSerializerForSubmit(ForeignKeyPersonalInfoMixin, LnAdGroupRelatedMixin, DetermineReadOnlyMix,
                                              RequestUploadFileMixin, MailToSerializerMixin, AbstractRequestSerializer):
    '''
    Serializer for Update Account Request - Submission
    '''

    def _get_if_readonly(self, instance, user):
        return not 'uam_requests.can_submit_update_request' in user.get_all_permissions()

    user_id = serializers.CharField(
        max_length=50, write_only=True, required=False)

    def _get_current_mail_status(self):
        return UpdateAccountRequest.STATUS_NEW

    class Meta:
        model = UpdateAccountRequest
        # fields = '__all__'
        read_only_fields = (
            'id', 'request_id', 'status',
            'creation_date', 'last_modification_date', 'submission_date', 'value_changes', 'ad_user_groups', 'ln_user_groups',
            'query_surname', 'query_given_name', 'query_post_title', 'query_status_desc', 'query_request_type_desc',
        )
        exclude = ('_ad_ps_magistrate_of_lt',)
        # extra_kwargs = {'account_effective_end_date': {'required': True}}

    def _get_required_fields_confirm(self):
        return ('account_effective_start_date', 'surname', 'title', 'given_name', 'uam_id')

    def _validate_confirm(self, data):
        if utils.compare_value(
                utils.get_field_value(
                    self.instance, data, 'account_effective_start_date'),
                utils.get_field_value(self.instance, data, 'account_effective_end_date')) > 0:
            raise serializers.ValidationError(
                'Account Effective Date range is not correct')
        return data

    def _allow_process(self, _data):
        if hasattr(self, 'instance'):
            return self.instance is None or self.instance.status == UpdateAccountRequest.STATUS_NEW
        return True

    def _update_draft(self, updated_instance, _validated_data):
        user_id = updated_instance.user_id
        updated_instance.related_user = UamUser.objects.get(pk=user_id)
        return updated_instance

    def _update_confirm(self, updated_instance, _validated_data):
        user_id = updated_instance.user_id
        updated_instance.related_user = UamUser.objects.get(pk=user_id)
        # updated_instance.submit()
        return updated_instance

    def _update_reject(self, updated_instance, _validated_data):
        updated_instance.withdraw()
        return updated_instance

    def _finalize_confirm(self, updated_instance: UpdateAccountRequest):
        '''
        The submit was called at this method instead of _update_confirm since submit will record all difference made to related_user.
        However, for the case of creation, all many-to-many relations will not be ready during _update_confirm since they can only exist
        after the pk of the request was created.  Thus, calling of submit was postponed to this method.
        '''
        updated_instance.submit()
        updated_instance.save()
        convert_accountrequest_send_mail(updated_instance, self.context.get(
            'request', None), UpdateAccountRequest.STATUS_NEW, ExternalSync.MAIL_TYPE_UPDATE_ACCOUNT_REVIEW)


class UpdateAccountRequestSerializerForReview(RelatedUserInfoMixin, ForeignKeyPersonalInfoMixin, LnAdGroupRelatedMixin, DetermineReadOnlyMix,
                                              RequestUploadFileMixin, MailToSerializerMixin, AbstractRequestSerializer):
    '''
    Serializer for Update Account Request - Review by ITOO
    '''

    def _get_if_readonly(self, instance, user):
        return (not ('uam_requests.can_review_update_request' in user.get_all_permissions())) or instance.status != UpdateAccountRequest.STATUS_PENDING_REVIEW_ITOO

    def _get_current_mail_status(self):
        return UpdateAccountRequest.STATUS_PENDING_REVIEW_ITOO

    class Meta:
        model = UpdateAccountRequest
        # fields = '__all__'
        read_only_fields = (
            'id', 'request_id', 'status',
            'creation_date', 'last_modification_date', 'submission_date', 'related_user', 'value_changes',
            'query_surname', 'query_given_name', 'query_post_title', 'query_status_desc', 'query_request_type_desc',
        )
        exclude = ('_ad_ps_magistrate_of_lt',)
        # extra_kwargs = {'account_effective_end_date': {'required': True}}

    def _get_required_fields_confirm(self):
        return ('account_effective_start_date', 'surname', 'title', 'given_name', 'user_id')

    def _validate_confirm(self, data):
        basic_rules = {}
        if utils.get_field_value(self.instance, data, 'oa_need_windows_login'):
            basic_rules['ad_windows_login_name'] = {'required': True}
        if utils.get_field_value(self.instance, data, 'oa_need_lotus_notes'):
            basic_rules['ln_lotus_notes_mail_name'] = {
                'required': True, 'display_name': 'Lotus Notes Mail name'}
        self._validate_data(data, basic_rules)
        if utils.compare_value(
                utils.get_field_value(
                    self.instance, data, 'account_effective_start_date'),
                utils.get_field_value(self.instance, data, 'account_effective_end_date')) > 0:
            raise serializers.ValidationError(
                'Account Effective Date range is not correct')
        # if utils.get_field_value(self.instance, data, 'oa_need_windows_login'):
        #     ad_login_name = utils.get_field_value(
        #         self.instance, data, 'ad_windows_login_name')
        #     if UamUser.objects.exclude(id=self.instance.user_id).filter(ad_windows_login_name=ad_login_name).exists():
        #         raise serializers.ValidationError(
        #             'Ad Login name %s already existed' % ad_login_name)
        prevent_account_exist(self.instance, data)
        return data

    def _get_required_fields_reject(self):
        return ('oth_other_justification',)

    def _allow_process(self, _data):
        return self.instance.status == UpdateAccountRequest.STATUS_PENDING_REVIEW_ITOO

    def _update_confirm(self, updated_instance, _validated_data):
        updated_instance.review()
        return updated_instance

    def _update_reject(self, updated_instance, _validated_data):
        updated_instance.reject_on_review()
        return updated_instance

    def _finalize_confirm(self, updated_instance: UpdateAccountRequest):
        convert_accountrequest_send_mail(updated_instance, self.context.get(
            'request', None), UpdateAccountRequest.STATUS_PENDING_REVIEW_ITOO, ExternalSync.MAIL_TYPE_UPDATE_ACCOUNT_EXECUTE)

    def _finalize_reject(self, updated_instance: UpdateAccountRequest):
        convert_accountrequest_send_mail(updated_instance, self.context.get(
            'request', None), UpdateAccountRequest.STATUS_PENDING_REVIEW_ITOO, ExternalSync.MAIL_TYPE_UPDATE_ACCOUNT_REJECTED_BY_ITOO)


class UpdateAccountRequestSerializerForExecute(RelatedUserInfoMixin, ForeignKeyPersonalInfoMixin, LnAdGroupRelatedMixin, DetermineReadOnlyMix,
                                               RequestUploadFileMixin, MailToSerializerMixin, AbstractRequestSerializer):
    '''
    Serializer for Update Account Request - Review/Execute by ITOT
    '''

    def _get_if_readonly(self, instance, user):
        return (not ('uam_requests.can_execute_update_request' in user.get_all_permissions())) or instance.status != UpdateAccountRequest.STATUS_PENDING_REVIEW_ITOT

    def _get_current_mail_status(self):
        return UpdateAccountRequest.STATUS_PENDING_REVIEW_ITOT

    class Meta:
        model = UpdateAccountRequest
        # fields = '__all__'
        read_only_fields = (
            'id', 'request_id', 'status', 'oth_other_request', 'oth_other_justification',
            'creation_date', 'last_modification_date', 'submission_date', 'related_user', 'value_changes',
            'query_surname', 'query_given_name', 'query_post_title', 'query_status_desc', 'query_request_type_desc',
        )
        exclude = ('_ad_ps_magistrate_of_lt', )

    def _get_required_fields_confirm(self):
        return ('account_effective_start_date',
                'surname', 'title', 'given_name', 'oa_need_windows_login', 'oa_need_lotus_notes',)

    def _validate_confirm(self, data):
        basic_rules = {
        }
        if utils.get_field_value(self.instance, data, 'oa_need_windows_login'):
            basic_rules['ad_windows_login_name'] = {'required': True}
        if utils.get_field_value(self.instance, data, 'oa_need_lotus_notes'):
            basic_rules['ln_lotus_notes_mail_name'] = {'required': True}
        self._validate_data(data, basic_rules)
        if utils.compare_value(
                utils.get_field_value(
                    self.instance, data, 'account_effective_start_date'),
                utils.get_field_value(self.instance, data, 'account_effective_end_date')) > 0:
            raise serializers.ValidationError(
                'Account Effective Date range is not correct')
        # if utils.get_field_value(self.instance, data, 'oa_need_windows_login'):
        #     ad_login_name = utils.get_field_value(
        #         self.instance, data, 'ad_windows_login_name')
        #     if UamUser.objects.exclude(id=self.instance.user_id).filter(ad_windows_login_name=ad_login_name).exists():
        #         raise serializers.ValidationError(
        #             'Ad Login name %s already existed' % ad_login_name)
        prevent_account_exist(self.instance, data)
        return data

    def _get_required_fields_reject(self):
        return ('oth_other_remark',)

    def _allow_process(self, _data):
        return self.instance.status == UpdateAccountRequest.STATUS_PENDING_REVIEW_ITOT

    def _update_confirm(self, updated_instance, _validated_data):
        updated_instance.execute()
        return updated_instance

    def _update_reject(self, updated_instance, _validated_data):
        updated_instance.reject_on_execute()
        return updated_instance

    def _finalize_confirm(self, updated_instance: UpdateAccountRequest):
        request = self.context.get('request', None)
        current_user = request.user if request else None
        convert_external_sync_for_remote(
            self.data, updated_instance, current_user)
        convert_accountrequest_send_mail(
            updated_instance, request, UpdateAccountRequest.STATUS_PENDING_REVIEW_ITOT, ExternalSync.MAIL_TYPE_UPDATE_ACCOUNT_COMPLETED)

    def _finalize_reject(self, updated_instance: UpdateAccountRequest):
        convert_accountrequest_send_mail(updated_instance, self.context.get(
            'request', None), UpdateAccountRequest.STATUS_PENDING_REVIEW_ITOT, ExternalSync.MAIL_TYPE_UPDATE_ACCOUNT_REJECTED_BY_ITOT)
