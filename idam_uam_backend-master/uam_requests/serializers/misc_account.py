from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from uam_requests.utils import (
    AccountInfoSerializerMixin, AbstractRequestSerializer,
    convert_external_sync_for_remote, convert_baserequest_send_mail,
)
from uam_requests.models import (BaseRequest, CreateAccountRequest, UpdateAccountRequest, ResetPasswordRequest,
                                 DisableAccountRequest, EnableAccountRequest, DeleteAccountRequest,)
from uam_requests.serializers.create_account import (CreateAccountRequestSerializer, CreateAccountRequestSerializerForExecute,
                                                     CreateAccountRequestSerializerForReview, CreateAccountRequestSerializerForSetupComplete,
                                                     CreateAccountRequestSerializerForSubmit, CreateAccountRequestSerializerForUserAck, )
from uam_requests.serializers.update_account import (UpdateAccountRequestSerializer, UpdateAccountRequestSerializerForExecute,
                                                     UpdateAccountRequestSerializerForReview, UpdateAccountRequestSerializerForSubmit, )

from uam_users.models import UamUser


class ResetPasswordRequestSerializer(AccountInfoSerializerMixin, AbstractRequestSerializer):
    '''
    Serializer for Reset Password Request
    '''
    class Meta:
        model = ResetPasswordRequest

        # fields = (
        #     'id', 'creation_date', 'last_modification_date', 'request_id', 'status', 'new_password', 'related_user',
        # )

        fields = '__all__'
        read_only_fields = (
            'id', 'creation_date', 'last_modification_date', 'request_id', 'status', 'submission_date',
            'query_surname', 'query_given_name', 'query_post_title', 'query_status_desc', 'query_request_type_desc',
        )

    def _get_required_fields_confirm(self):
        return ('new_password',)
    # def _validate_confirm(self, data):
    #     basic_rules = {
    #         'new_password': {'required': True}
    #     }
    #     self._validate_data(data, basic_rules)
    #     return data

    def _update_confirm(self, updated_instance, _validated_data):
        updated_instance.reset_password()
        return updated_instance

    def _finalize_confirm(self, updated_instance):
        request = self.context.get('request', None)
        current_user = request.user if request else None
        convert_external_sync_for_remote(None, updated_instance, current_user)
        convert_baserequest_send_mail(updated_instance, request)


class DisableAccountRequestSerializer(AccountInfoSerializerMixin, AbstractRequestSerializer):
    '''
    Serializer for Disable Account Request
    '''
    user_ids = serializers.CharField(
        max_length=50, write_only=True, required=False)

    class Meta:
        model = DisableAccountRequest
        '''
        fields = (
            'id', 'submission_date', 'last_modification_date', 'request_id', 'status','user_id', 'user_ids','related_user',
        )
        '''
        fields = '__all__'
        read_only_fields = (
            'id', 'submission_date', 'last_modification_date', 'request_id', 'status', 'user_id', 'user_ids', 'related_user',
        )

    def _get_required_fields_confirm(self):
        return ('user_ids')

    def _update_confirm(self, disable_instance, validated_data):
        user_ids = validated_data['user_ids']
        disable_instance.user_id = user_ids
        disable_instance.related_user = UamUser.objects.get(pk=user_ids)
        disable_instance.disable_account()
        return disable_instance

    def _finalize_confirm(self, disable_instance):
        request = self.context.get('request', None)
        current_user = request.user if request else None
        convert_external_sync_for_remote(None, disable_instance, current_user)
        convert_baserequest_send_mail(disable_instance, request)


class EnableAccountRequestSerializer(AccountInfoSerializerMixin, AbstractRequestSerializer):
    '''
    Serializer for Enable Account Request
    '''
    user_ids = serializers.CharField(
        max_length=50, write_only=True, required=False)

    class Meta:
        model = EnableAccountRequest
        '''
        fields = (
            'id', 'submission_date', 'last_modification_date', 'request_id', 'status','user_id', 'user_ids','related_user',
        )
        '''
        fields = '__all__'
        read_only_fields = (
            'id', 'submission_date', 'last_modification_date', 'request_id', 'status', 'user_id', 'user_ids', 'related_user',
        )

    def _get_required_fields_confirm(self):
        return ('user_ids')

    def _update_confirm(self, enable_instance, validated_data):
        user_ids = validated_data['user_ids']
        enable_instance.user_id = user_ids
        enable_instance.related_user = UamUser.objects.get(pk=user_ids)
        enable_instance.enable_account()
        return enable_instance

    def _finalize_confirm(self, enable_instance):
        request = self.context.get('request', None)
        current_user = request.user if request else None
        convert_external_sync_for_remote(None, enable_instance, current_user)
        convert_baserequest_send_mail(enable_instance, request)


class DeleteAccountRequestSerializer(AccountInfoSerializerMixin, AbstractRequestSerializer):
    '''
    Serializer for Delete Account Request
    '''
    user_ids = serializers.CharField(
        max_length=50, write_only=True, required=False)

    class Meta:
        model = DeleteAccountRequest
        '''
        fields = (
            'id', 'submission_date', 'last_modification_date', 'request_id', 'status','user_id', 'user_ids','related_user',
        )
        '''
        fields = '__all__'
        read_only_fields = (
            'id', 'submission_date', 'last_modification_date', 'request_id', 'status', 'user_id', 'user_ids', 'related_user',
        )

    def _get_required_fields_confirm(self):
        return ('user_ids')

    def _update_confirm(self, instance, validated_data):
        user_ids = validated_data['user_ids']
        instance.user_id = user_ids
        instance.related_user = UamUser.objects.get(pk=user_ids)
        instance.delete_account()
        return instance

    def _finalize_confirm(self, instance):
        request = self.context.get('request', None)
        convert_baserequest_send_mail(instance, request)


class BasicBaseRequestSerializer(PolymorphicSerializer):
    '''
    Generic Request Serializer for listing all user related requests
    '''

    def to_representation(self, obj):
        to_rep = super().to_representation(obj)
        if obj.related_user:
            to_rep.update({'uam_id': obj.related_user.uam_id})
        to_rep.update({'request_status_name': obj.query_status_desc})
        to_rep.update({'request_type_name': obj.query_request_type_desc})
        return to_rep

    model_serializer_mapping = {
        CreateAccountRequest: CreateAccountRequestSerializer,
        UpdateAccountRequest: UpdateAccountRequestSerializer,
        ResetPasswordRequest: ResetPasswordRequestSerializer,
        DisableAccountRequest: DisableAccountRequestSerializer,
        EnableAccountRequest: EnableAccountRequestSerializer,
        DeleteAccountRequest: DeleteAccountRequestSerializer,
    }


class BaseRequestSerializer(BasicBaseRequestSerializer):
    '''
    Generic Request Serializer for all user related requests
    '''
    model_serializer_mapping = {
        CreateAccountRequest: {
            BaseRequest.STATUS_NEW: CreateAccountRequestSerializerForSubmit,
            BaseRequest.STATUS_WITHDRAWN: CreateAccountRequestSerializerForSubmit,
            BaseRequest.STATUS_PENDING_REVIEW_ITOO: CreateAccountRequestSerializerForReview,
            BaseRequest.STATUS_PENDING_REVIEW_ITOT: CreateAccountRequestSerializerForExecute,
            BaseRequest.STATUS_CONFIRMED_BY_HELPDESK: CreateAccountRequestSerializerForSetupComplete,
            BaseRequest.STATUS_REJECTED_BY_ITOO: CreateAccountRequestSerializerForReview,
            BaseRequest.STATUS_REJECTED_BY_ITOT: CreateAccountRequestSerializerForExecute,
            BaseRequest.STATUS_SETUP_COMPLETED: CreateAccountRequestSerializerForUserAck,
            BaseRequest.STATUS_USER_ACK: CreateAccountRequestSerializerForUserAck},
        UpdateAccountRequest: {
            BaseRequest.STATUS_NEW: UpdateAccountRequestSerializerForSubmit,
            BaseRequest.STATUS_WITHDRAWN: UpdateAccountRequestSerializerForSubmit,
            BaseRequest.STATUS_PENDING_REVIEW_ITOO: UpdateAccountRequestSerializerForReview,
            BaseRequest.STATUS_REJECTED_BY_ITOO: UpdateAccountRequestSerializerForReview,
            BaseRequest.STATUS_REJECTED_BY_ITOT: UpdateAccountRequestSerializerForExecute,
            BaseRequest.STATUS_PENDING_REVIEW_ITOT: UpdateAccountRequestSerializerForExecute,
            BaseRequest.STATUS_UPDATE_COMPLETED: UpdateAccountRequestSerializerForExecute
        },
        ResetPasswordRequest: ResetPasswordRequestSerializer,
        DisableAccountRequest: DisableAccountRequestSerializer,
        EnableAccountRequest: EnableAccountRequestSerializer,
        DeleteAccountRequest: DeleteAccountRequestSerializer,
    }

    def _get_serializer_from_model_or_instance(self, model_or_instance):
        model = self._to_model(model_or_instance)
        # print(model_or_instance)
        for klass in model.mro():
            if klass in self.model_serializer_mapping:
                tmp = self.model_serializer_mapping[klass]
                if isinstance(tmp, serializers.Serializer):
                    return tmp
                else:
                    if model_or_instance.status in tmp:
                        # return tmp[model_or_instance.status](instance=model_or_instance)
                        return tmp[model_or_instance.status](instance=model_or_instance, context=self.context)

        raise KeyError(
            '`{cls}.model_serializer_mapping` is missing '
            'a corresponding serializer for `{model}` model'.format(
                cls=self.__class__.__name__,
                model=model.__name__
            )
        )


class BaseRequestListSerializer(serializers.ModelSerializer):
    section = serializers.SerializerMethodField()

    class Meta:
        model = BaseRequest
        fields = (
            'id', 'request_id', 'query_surname', 'query_given_name', 'section', 'query_post_title', 'submission_date',
            'query_request_type_desc', 'query_status_desc', 'creation_date', 'last_modification_date',
        )

    def get_section(self, instance):
        return {'id': instance['section__id'], 'code': instance['section__code']}
