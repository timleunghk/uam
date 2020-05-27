from django.db import transaction
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from codetables.serializers import SectionSerializer
from uam_requests.models import BaseRequest
from uam_requests.permissions import can_maintain_all_section
from uam_requests import models
from common.utils import DateTimeFieldWithTZ
from common import utils
from common import jud_auth
from common.exceptions import ConcurrentUpdate, MissingLastModificationDate
from .serializer_mixins import DisableConcurrentCheckMixin


class AbstractRequestSerializer(serializers.ModelSerializer):
    section = SectionSerializer(many=False, read_only=True)

    creation_date = DateTimeFieldWithTZ(read_only=True)
    # last_modification_date = DateTimeFieldWithTZ(read_only=True)
    # Accept last_modification_date for checking concurrent update.
    last_modification_date = DateTimeFieldWithTZ(required=False)
    # submission_date = serializers.DateField(format=DATE_FORMAT, read_only=True)
    request_status_name = serializers.SerializerMethodField()
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

    def get_request_status_name(self, value):
        return BaseRequest.REQUEST_STATUSES[value.status][1]

    CURRENT_ACTION_KEY = 'current_action'

    CONFIRM_KEY = 'confirm'

    # def __init__(self, *args, **kwargs):
    #     super(AbstractRequestSerializer, self).__init__(*args, **kwargs)
    #     self._get_required_fields()

    def _validate_data(self, data, rules_dict):
        def _convert_field_name_to_display_name(instr):
            return ' '.join(x.capitalize() for x in instr.split('_'))

        def _validate_existence(value):
            if isinstance(value, bool):
                return True
            if isinstance(value, str):
                value = value.strip()
            return bool(value)

        errors = []
        for field_name, _rule in rules_dict.items():
            if 'required' in rules_dict[field_name] and rules_dict[field_name]['required']:
                if field_name in data:
                    result = _validate_existence(data[field_name])
                else:
                    result = _validate_existence(
                        utils.get_field_value(self.instance, data, field_name))
                if not result:
                    display_name = rules_dict[field_name].get(
                        'display_name', _convert_field_name_to_display_name(field_name))
                    errors.append('%s shall not be empty' % display_name)
        if errors:
            raise serializers.ValidationError(errors)

    def _get_methods(self, action_prefix):
        result = []
        if self.CURRENT_ACTION_KEY in self.context:
            for action_name in self.context[self.CURRENT_ACTION_KEY]:
                method_name = '%s_%s' % (action_prefix, action_name)
                if callable(getattr(self, method_name, None)):
                    result.append(getattr(self, method_name))
        else:
            method_name = '%s_%s' % (action_prefix, self.CONFIRM_KEY)
            if callable(getattr(self, method_name, None)):
                result.append(getattr(self, method_name))
        return result

    def _allow_process(self, _data):
        '''
        Subclass shall override this to check if current action could be performed.
        E.g. If reviewing request, check if current instance is in 'PENDING_FOR_REVIEW' state
        # Returns:
            True if allowed, False if not
        '''
        return True

    def _save_instance(self, updated_instance, validated_data):
        method_list = self._get_methods('_update')
        for method in method_list:
            updated_instance = method(updated_instance, validated_data)
        request = self.context.get('request', None)
        if not can_maintain_all_section(request):
            # updated_instance.section_id = request.session.get(
            #     jud_auth.SAML_SESSION_USER_SECTION, None)
            updated_instance.section_id = request.session.get(
                jud_auth.SAML_SESSION_USER_SECTION, None)['code']
        updated_instance.save()
        return updated_instance

    def _pre_save(self, _validated_data, _instance):
        '''
        NOTE:
        Pre_save will be called before actual update of the instance
        E.g. Normally, this method will pop some non-standard field from 
            validated_data and return them for post_save to process
        '''
        return {}

    def _post_save(self, _validated_data, updated_instance, _pre_save_dict):
        '''
        NOTE:
        All additional operation that require update_instance was persist (i.e. id/pk field is not null) shall reside at this
        For the case of creation, post_save will be called right 
            after the actual updated_instance was saved.  
        For the case of update, post_save will be called before the actual updated_instance
            was saved since the actual save action (i.e. _save_instance) may require some
            finalized value from post_save (e.g. When updating to UamUser, _save_instance 
            will copy all fields, even update from post_save to UamUser )
        ##TODO May need to refactor this
        '''
        return updated_instance

    @transaction.atomic
    def create(self, validated_data):
        # Get all method starts with _initialize for current action and execute them
        # e.g. _initialize_draft when saving draft, _initialize_confirm for confirming, _initialize_reject for reject
        methodlist = self._get_methods('_initialize')
        for method in methodlist:
            method(None, validated_data)
        # Call _pre_save -> _save_instance -> _post_save
        pre_save_dict = self._pre_save(validated_data, None)
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            validated_data['creation_user'] = request.user
            validated_data['last_modification_user'] = request.user
        updated_instance = self._save_instance(
            super(AbstractRequestSerializer, self).create(validated_data), validated_data)
        updated_instance = self._post_save(
            validated_data, updated_instance, pre_save_dict)
        # Get all method starts with _finalize for current action and execute them
        # e.g. _finalize_draft when saving draft, _finalize_confirm for confirming, _finalize_reject for reject
        methodlist = self._get_methods('_finalize')
        for method in methodlist:
            method(updated_instance)
        # Write audit log
        self.write_audit_log(updated_instance)
        return updated_instance

    @transaction.atomic
    def update(self, instance, validated_data):
        print(validated_data)
        # Get all method starts with _initialize for current action and execute them
        # e.g. _initialize_draft when saving draft, _initialize_confirm for confirming, _initialize_reject for reject
        methodlist = self._get_methods('_initialize')
        for method in methodlist:
            method(instance, validated_data)
        if not isinstance(self, DisableConcurrentCheckMixin):
            # Check for concurrent update by using last_modification_date as optimistic lock
            last_modification_date = validated_data.pop(
                'last_modification_date', None)
            if last_modification_date:
                if (instance.last_modification_date - last_modification_date).total_seconds() >= 1:
                    raise ConcurrentUpdate()
            else:
                raise MissingLastModificationDate()

        # Call _pre_save -> _post_save -> _save_instance
        pre_save_dict = self._pre_save(validated_data, instance)
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            validated_data['last_modification_user'] = request.user
        # updated_instance = self._save_instance(super(
        #     AbstractRequestSerializer, self).update(instance, validated_data), validated_data)
        updated_instance = self._post_save(
            validated_data, instance, pre_save_dict)
        updated_instance = self._save_instance(super(
            AbstractRequestSerializer, self).update(updated_instance, validated_data), validated_data)
        # Get all method starts with _finalize for current action and execute them
        # e.g. _finalize_draft when saving draft, _finalize_confirm for confirming, _finalize_reject for reject
        methodlist = self._get_methods('_finalize')
        for method in methodlist:
            method(updated_instance)
        # Write audit log
        self.write_audit_log(updated_instance)
        return updated_instance

    def validate(self, data):
        if not self._allow_process(data):
            raise serializers.ValidationError(
                'The action could not be performed since the request is not in correct state')
        method_list = self._get_methods('_validate')
        for method in method_list:
            data = method(data)
        return data

    def get_extra_kwargs(self):
        extra_kwargs = super(AbstractRequestSerializer,
                             self).get_extra_kwargs()
        method_list = self._get_methods('_get_required_fields')
        for method in method_list:
            field_lists = method()
            for field_name in field_lists:
                fieldmap = extra_kwargs.get(field_name, {})
                fieldmap['required'] = True
                extra_kwargs[field_name] = fieldmap
        return extra_kwargs

    def write_audit_log(self, updated_instance):
        # config = { 'AMQP_URI': settings.AMQP_URI }
        method = self.context['request'].method
        path = self.context['request'].path
        # user = self.context['request'].user
        # extra_info = {'src_http_method': method, 'src_http_path': path,
        #     'src_log_time': datetime.datetime.now().isoformat(), 'log_version': 0.1}
        extra_info = {'src_http_method': method, 'src_http_path': path,
                      'log_version': 0.1}
        tmp_serializer = self.__class__(updated_instance)
        out_data = {**tmp_serializer.data, **extra_info}
        _audit_rec = models.AuditLog.objects.create(
            audit_log_data=JSONRenderer().render(out_data).decode('utf8'))
        # with utils.get_nameko_client_for_audit_log() as client:
        #     tmp_serializer = self.__class__(updated_instance)
        #     result = client.idam_audit_log_service.write_log(tmp_serializer.data, extra_info)
