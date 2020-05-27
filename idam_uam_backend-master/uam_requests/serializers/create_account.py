from rest_framework import serializers
from uam_requests.utils import (
    ForeignKeyPersonalInfoMixin, DetermineReadOnlyMix, RequestUploadFileMixin,
    MailToSerializerMixin, AbstractRequestSerializer, LnAdGroupRelatedMixin,
    DisableConcurrentCheckMixin, prevent_account_exist, convert_external_sync_for_remote,
    convert_accountrequest_send_mail,
)
from uam_requests.models import CreateAccountRequest
from uam_users.serializers import UamUserSerializer
from codetables.serializers import SectionSerializer
from common import utils
from interface.models import ExternalSync


class CreateAccountRequestSerializerForSubmit(ForeignKeyPersonalInfoMixin, DetermineReadOnlyMix, RequestUploadFileMixin,
                                              MailToSerializerMixin, AbstractRequestSerializer):
    '''
    Serializer for Create Account for submission
    '''

    def _get_if_readonly(self, _instance, user):
        return not 'uam_requests.can_submit_create_request' in user.get_all_permissions()

    def _get_current_mail_status(self):
        return CreateAccountRequest.STATUS_NEW

    class Meta:
        model = CreateAccountRequest
        # fields = '__all__'
        read_only_fields = (
            'id', 'creation_date', 'last_modification_date', 'request_id', 'status',
            'creation_date', 'last_modification_date', 'submission_date', 'related_user',
            'query_surname', 'query_given_name', 'query_post_title',
            'ad_user_groups', 'ln_user_groups',
        )
        exclude = ('_ad_ps_magistrate_of_lt',)
        # extra_kwargs = {'account_effective_end_date': {'required': True}}

    def _get_required_fields_confirm(self):
        return ('account_effective_start_date', 'surname', 'title', 'given_name',)

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
            return self.instance is None or self.instance.status == CreateAccountRequest.STATUS_NEW
        return True

    def _update_confirm(self, updated_instance, _validated_data):
        updated_instance.submit()
        return updated_instance

    def _update_reject(self, updated_instance, _validated_data):
        updated_instance.withdraw()
        return updated_instance

    def _finalize_confirm(self, updated_instance: CreateAccountRequest):
        convert_accountrequest_send_mail(updated_instance, self.context.get(
            'request', None), CreateAccountRequest.STATUS_NEW, ExternalSync.MAIL_TYPE_CREATE_ACCOUNT_REVIEW)


class CreateAccountRequestSerializerForReview(
    ForeignKeyPersonalInfoMixin, LnAdGroupRelatedMixin, DetermineReadOnlyMix, RequestUploadFileMixin,
    MailToSerializerMixin, AbstractRequestSerializer
):
    '''
    Serializer for Create Account for Review by ITOO
    '''

    def _get_if_readonly(self, instance, user):
        return (not ('uam_requests.can_review_create_request' in user.get_all_permissions())) or instance.status != CreateAccountRequest.STATUS_PENDING_REVIEW_ITOO

    def _get_current_mail_status(self):
        return CreateAccountRequest.STATUS_PENDING_REVIEW_ITOO

    class Meta:
        model = CreateAccountRequest
        # fields = '__all__'
        read_only_fields = (
            'id', 'request_id', 'status', 'oth_other_request',
            'creation_date', 'last_modification_date', 'submission_date', 'related_user',
            'query_surname', 'query_given_name', 'query_post_title', 'query_status_desc', 'query_request_type_desc',
        )
        exclude = ('_ad_ps_magistrate_of_lt',)

    def _get_required_fields_confirm(self):
        return ('account_effective_start_date', 'surname', 'title',
                'given_name', 'oa_need_windows_login', 'oa_need_lotus_notes')

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
        prevent_account_exist(self.instance, data)
        return data

    def _get_required_fields_reject(self):
        return ('oth_other_justification',)

    def _allow_process(self, _data):
        return self.instance.status == CreateAccountRequest.STATUS_PENDING_REVIEW_ITOO

    def _update_confirm(self, updated_instance, _validated_data):
        updated_instance.review()
        return updated_instance

    def _update_reject(self, updated_instance, _validated_data):
        updated_instance.reject_on_review()
        return updated_instance

    def _finalize_confirm(self, updated_instance: CreateAccountRequest):
        convert_accountrequest_send_mail(updated_instance, self.context.get(
            'request', None), CreateAccountRequest.STATUS_PENDING_REVIEW_ITOO, ExternalSync.MAIL_TYPE_CREATE_ACCOUNT_EXECUTE)

    def _finalize_reject(self, updated_instance: CreateAccountRequest):
        convert_accountrequest_send_mail(updated_instance, self.context.get(
            'request', None), CreateAccountRequest.STATUS_PENDING_REVIEW_ITOO, ExternalSync.MAIL_TYPE_CREATE_ACCOUNT_REJECTED_BY_ITOO)


class CreateAccountRequestSerializerForExecute(
        ForeignKeyPersonalInfoMixin, LnAdGroupRelatedMixin, DetermineReadOnlyMix,
        RequestUploadFileMixin, MailToSerializerMixin, AbstractRequestSerializer
):
    '''
    Serializer for Create Account (Review/Execute by ITOT)
    '''
    related_user = UamUserSerializer(many=False, read_only=True)

    def _get_current_mail_status(self):
        return CreateAccountRequest.STATUS_PENDING_REVIEW_ITOT

    def _get_if_readonly(self, instance, user):
        return (not ('uam_requests.can_execute_create_request' in user.get_all_permissions())) or instance.status != CreateAccountRequest.STATUS_PENDING_REVIEW_ITOT

    class Meta:
        model = CreateAccountRequest
        # fields = '__all__'
        read_only_fields = (
            'id', 'request_id', 'status', 'oth_other_request', 'oth_other_justification',
            'creation_date', 'last_modification_date', 'submission_date', 'related_user',
            'query_surname', 'query_given_name', 'query_post_title', 'query_status_desc', 'query_request_type_desc',
        )
        exclude = ('_ad_ps_magistrate_of_lt',)

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
        prevent_account_exist(self.instance, data)
        return data

    def _get_required_fields_reject(self):
        return ('oth_other_remark',)

    def _allow_process(self, _data):
        return self.instance.status == CreateAccountRequest.STATUS_PENDING_REVIEW_ITOT

    def _update_confirm(self, updated_instance, _validated_data):
        updated_instance.execute()
        return updated_instance

    def _update_reject(self, updated_instance, _validated_data):
        updated_instance.reject_on_execute()
        return updated_instance

    def _finalize_confirm(self, updated_instance):
        request = self.context.get('request', None)
        current_user = request.user if request else None
        convert_external_sync_for_remote(
            self.data, updated_instance, current_user)
        convert_accountrequest_send_mail(updated_instance, self.context.get(
            'request', None), CreateAccountRequest.STATUS_PENDING_REVIEW_ITOT, ExternalSync.MAIL_TYPE_CREATE_ACCOUNT_EXECUTE)
        # mail_to = RequestMailTo.objects.get(
        #     request=updated_instance, status=CreateAccountRequest.STATUS_PENDING_REVIEW_ITOT)
        # data = {
        #     'to': mail_to.to,
        #     'cc': mail_to.cc,
        #     'surname': updated_instance.surname,
        #     'given_name': updated_instance.given_name,
        #     'section': updated_instance.section.code,
        #     'rank': updated_instance.master_rank.value,
        #     'substantive_rank': updated_instance.substantive_rank.value,
        #     'request_id': updated_instance.request_id,
        #     'post_title': updated_instance.post_title,
        #     'mail_type': ExternalSync.MAIL_TYPE_CREATE_ACCOUNT_EXECUTE,
        # }
        # convert_send_mail(data, updated_instance, current_user)

    def _finalize_reject(self, updated_instance: CreateAccountRequest):
        convert_accountrequest_send_mail(updated_instance, self.context.get(
            'request', None), CreateAccountRequest.STATUS_PENDING_REVIEW_ITOT, ExternalSync.MAIL_TYPE_CREATE_ACCOUNT_REJECTED_BY_ITOT)
        # mail_to = RequestMailTo.objects.get(
        #     request=updated_instance, status=CreateAccountRequest.STATUS_PENDING_REVIEW_ITOT)
        # data = {
        #     'to': mail_to.to,
        #     'cc': mail_to.cc,
        #     'surname': updated_instance.surname,
        #     'given_name': updated_instance.given_name,
        #     'request_id': updated_instance.request_id,
        #     'post_title': updated_instance.post_title,
        #     'mail_type': ExternalSync.MAIL_TYPE_CREATE_ACCOUNT_REJECTED_BY_ITOT,
        # }
        # request = self.context.get('request', None)
        # current_user = request.user if request else None
        # convert_send_mail(data, updated_instance, current_user)


class CreateAccountRequestSerializerForSetupComplete(DisableConcurrentCheckMixin, AbstractRequestSerializer):
    '''
    Serializer for Setup completion of Create Account
    '''
    class Meta:
        model = CreateAccountRequest
        fields = '__all__'
        read_only_fields = (
            'id', 'account_effective_start_date', 'account_effective_end_date', 'title', 'surname', 'given_name', 'request_id',
            'surname_chinese', 'given_name_chinese', 'prefered_name',
            'status', 'oth_other_request', 'oth_other_justification', 'oa_need_windows_login', 'ad_windows_login_name',
            'ad_is_magistrate_of_lt', 'ad_ps_magistrate_of_lt', 'ad_windows_first_name', 'ad_windows_last_name',
            'oa_need_lotus_notes', 'ln_lotus_notes_mail_name', 'ad_user_groups', 'ln_user_groups',
            'ln_middle_name', 'ln_first_name', 'ln_last_name',
            'ln_is_internet_mail_user', 'ln_is_gcn_user', 'ln_is_inote_user', 'ln_is_confidential_mail_user', 'ln_is_contractor',
            'creation_date', 'last_modification_date', 'submission_date', 'related_user',
            'query_surname', 'query_given_name', 'query_post_title', 'query_status_desc', 'query_request_type_desc',
        )

    def _allow_process(self, _data):
        return self.instance.status == CreateAccountRequest.STATUS_CONFIRMED_BY_HELPDESK

    def _update_confirm(self, updated_instance, _validated_data):
        updated_instance.set_up_complete()
        return updated_instance


class CreateAccountRequestSerializerForUserAck(DisableConcurrentCheckMixin, AbstractRequestSerializer):
    '''
    Serializer for Create Account - User Acknowledgement
    '''
    class Meta:
        model = CreateAccountRequest
        fields = '__all__'
        read_only_fields = (
            'id', 'account_effective_start_date', 'account_effective_end_date', 'title', 'surname', 'given_name', 'creation_date',
            'surname_chinese', 'given_name_chinese', 'prefered_name',
            'last_modification_date', 'request_id', 'status', 'oth_other_request', 'oth_other_justification', 'oa_need_windows_login',
            'ad_is_magistrate_of_lt', 'ad_ps_magistrate_of_lt', 'ad_windows_first_name', 'ad_windows_last_name',
            'ad_windows_login_name', 'oa_need_lotus_notes', 'ln_lotus_notes_mail_name', 'ad_user_groups', 'ln_user_groups',
            'ln_middle_name', 'ln_first_name', 'ln_last_name',
            'ln_is_internet_mail_user', 'ln_is_gcn_user', 'ln_is_inote_user', 'ln_is_confidential_mail_user', 'ln_is_contractor',
            'creation_date', 'last_modification_date', 'submission_date', 'related_user',
            'query_surname', 'query_given_name', 'query_post_title', 'query_status_desc', 'query_request_type_desc',
        )

    def _allow_process(self, _data):
        return self.instance.status == CreateAccountRequest.STATUS_SETUP_COMPLETED

    def _update_confirm(self, updated_instance, _validated_data):
        updated_instance.user_ack()
        return updated_instance


class CreateAccountRequestSerializer(serializers.ModelSerializer):
    section = SectionSerializer(many=False, read_only=True)

    '''
    Generic Serializer for Create Account Request
    '''
    class Meta:
        model = CreateAccountRequest
        fields = '__all__'
