# import json
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from common import utils
from interface.models import ExternalSync
from uam_users.models import UamUser
from uam_requests.models import (
    AccountRequest, RequestMailTo, BaseRequest,
    ResetPasswordRequest, EnableAccountRequest, DisableAccountRequest,
    DeleteAccountRequest,
)


def prevent_account_exist(instance, data):
    qs = UamUser.objects.all()
    if hasattr(instance, 'related_user'):
        if instance.related_user:
            qs = qs.exclude(id=instance.related_user.id)
    error_map = {}
    if utils.get_field_value(instance, data, 'oa_need_windows_login'):
        ad_login_name = utils.get_field_value(
            instance, data, 'ad_windows_login_name')
        if qs.filter(ad_windows_login_name=ad_login_name).exists():
            error_map['Windows Login Name'] = [
                'Ad Login name %s already existed' % ad_login_name]
    if utils.get_field_value(instance, data, 'oa_need_lotus_notes'):
        login_name = utils.get_field_value(
            instance, data, 'ln_lotus_notes_mail_name')
        if qs.filter(ln_lotus_notes_mail_name=login_name).exists():
            error_map['Lotus Note Account'] = [
                'Account name %s already existed' % login_name]
    if utils.get_field_value(instance, data, 'oa_need_dp'):
        login_name = utils.get_field_value(
            instance, data, 'dp_login_id')
        if qs.filter(dp_login_id=login_name).exists():
            error_map['DP Login ID'] = [
                'Account name %s already existed' % login_name]
    if utils.get_field_value(instance, data, 'oa_need_jjo'):
        login_name = utils.get_field_value(
            instance, data, 'jjo_login_id')
        if qs.filter(jjo_login_id=login_name).exists():
            error_map['JJO Portal Login ID'] = [
                'Account name %s already existed' % login_name]
    if error_map:
        raise serializers.ValidationError(error_map)


def _create_external_sync_rec(data, sync_type, sync_action, request, current_user):
    ExternalSync.objects.create(
        sync_data=JSONRenderer().render(data).decode(),
        sync_type=sync_type,
        sync_action=sync_action,
        request=request,
        creation_user=current_user,
        last_modification_user=current_user,
    )


def _convert_send_mail(data, request, current_user):
    _create_external_sync_rec(
        data, ExternalSync.SYNC_NOTES, ExternalSync.SYNC_ACTION_SEND_MAIL, request, current_user)


def convert_baserequest_send_mail(instance: BaseRequest, request):
    send_mail_type = None
    if isinstance(instance, ResetPasswordRequest):
        send_mail_type = ExternalSync.MAIL_TYPE_RESET_PASSWORD_TO_OWNER
    elif isinstance(instance, DisableAccountRequest):
        send_mail_type = ExternalSync.MAIL_TYPE_DISABLED_ACCOUNT_TO_OWNER
    elif isinstance(instance, EnableAccountRequest):
        send_mail_type = ExternalSync.MAIL_TYPE_ENABLED_ACCOUNT_TO_OWNER
    elif isinstance(instance, DeleteAccountRequest):
        send_mail_type = ExternalSync.MAIL_TYPE_DELETED_ACCOUNT_TO_OWNER
    data = {
        'surname': instance.query_surname,
        'given_name': instance.query_given_name,
        'post_title': instance.query_post_title,
        'mail_type': send_mail_type,
    }
    if send_mail_type:
        current_user = request.user if request else None
        _convert_send_mail(data, instance, current_user)


def convert_accountrequest_send_mail(instance: AccountRequest, request, mail_status, send_mail_type):
    mail_to = RequestMailTo.objects.get(
        request=instance, status=mail_status)
    data = {
        'to': mail_to.to,
        'cc': mail_to.cc,
        'surname': instance.surname,
        'given_name': instance.given_name,
        'section': instance.section.code if instance.section else None,
        'rank': instance.master_rank.value if instance.master_rank else None,
        'substantive_rank': instance.substantive_rank.value if instance.substantive_rank else None,
        'request_id': instance.request_id,
        'post_title': instance.post_title,
        'mail_type': send_mail_type,
    }
    if hasattr(instance, 'value_changes'):
        data['changes'] = instance.value_changes
    current_user = request.user if request else None
    _convert_send_mail(data, instance, current_user)


def convert_external_sync_for_remote(uam_request_dict, request, current_user):

    def _create_external_sync(data_switch, field_name_prefix, sync_type):
        data = []
        action = -1
        if isinstance(request, AccountRequest):
            if hasattr(request, 'value_changes'):
                ''' Update Account Request '''
                data_switch_changed = False
                for data_dict in request.value_changes:
                    fieldname = data_dict.get('field', '')
                    if fieldname.startswith(field_name_prefix) or fieldname == data_switch:
                        if fieldname == data_switch:
                            data_switch_changed = True
                        data.append(data_dict)
                if not data_switch_changed:
                    if not getattr(request, data_switch):
                        data = []
                    else:
                        action = ExternalSync.SYNC_ACTION_AMEND_ACCOUNT
                else:
                    if getattr(request, data_switch):
                        action = ExternalSync.SYNC_ACTION_UPSERT_ACCOUNT
                        data = [
                            {'field': key, 'to': value} for key, value in uam_request_dict.items() if key.startswith(field_name_prefix)
                        ]
                    else:
                        '''
                        Disabled the tab (e.g. AD, JJO, DP, Notes)
                        '''
                        action = ExternalSync.SYNC_ACTION_DISABLE_ACCOUNT

            else:
                ''' Create Account Request '''
                if uam_request_dict.get(data_switch, None):
                    data = [
                        {'field': key, 'to': value} for key, value in uam_request_dict.items() if key.startswith(field_name_prefix)
                    ]
                    action = ExternalSync.SYNC_ACTION_CREATE_ACCOUNT
        elif isinstance(request, ResetPasswordRequest):
            if getattr(request.related_user, data_switch, None) and data_switch == 'oa_need_windows_login':
                action = ExternalSync.SYNC_ACTION_RESET_PASSWORD
                data = {'new_password': request.new_password}
        elif isinstance(request, DisableAccountRequest):
            if getattr(request.related_user, data_switch, None):
                action = ExternalSync.SYNC_ACTION_DISABLE_ACCOUNT
                data = [ExternalSync.SYNC_ACTION_DISABLE_ACCOUNT]
        elif isinstance(request, EnableAccountRequest):
            if getattr(request.related_user, data_switch, None):
                action = ExternalSync.SYNC_ACTION_ENABLE_ACCOUNT
                data = [ExternalSync.SYNC_ACTION_ENABLE_ACCOUNT]
        elif isinstance(request, DeleteAccountRequest):
            pass
        if data:
            _create_external_sync_rec(
                data, sync_type, action, request, current_user)

    _create_external_sync('oa_need_windows_login', 'ad_', ExternalSync.SYNC_AD)
    _create_external_sync('oa_need_lotus_notes', 'ln_',
                          ExternalSync.SYNC_NOTES)
    _create_external_sync('oa_need_jjo', 'jjo_', ExternalSync.SYNC_JJO_PORTAL)
    _create_external_sync('oa_need_dp', 'dp_', ExternalSync.SYNC_DEPT_PORTAL)
