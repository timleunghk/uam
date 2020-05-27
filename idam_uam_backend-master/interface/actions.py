import json
from django.utils import timezone
from nameko.standalone.rpc import ClusterRpcProxy
from interface.models import ExternalSync
from uam_requests.models import BaseRequest, AccountRequest


def sync_jjo(sync_client: ClusterRpcProxy, sync_rec: ExternalSync):

    def _format_account_map(req: AccountRequest):

        def _format_full_name(request: AccountRequest):
            return ' '.join([rec for rec in [request.jjo_last_name, request.jjo_first_name] if rec])

        def _format_mail(request: AccountRequest):
            if request.jjo_email:
                return '@'.join([request.jjo_email, request.jjo_mail_domain.name])
            return None

        sync_map = {
            'cn': req.jjo_login_id,
            'JUDUserJJO': req.jjo_login_id,
            'loginDisabled': False,
            'sn': req.jjo_last_name,
            'description': req.post_title,
            'givenName': req.jjo_first_name,
            'fullName': _format_full_name(req),
            'employeeType': req.jjo_emp_type.name if req.jjo_emp_type else None,
            'employeeNumber': req.related_user.uam_id if req.related_user else None,
            # 'initials': None,
            # 'Language': None,
            'mail': _format_mail(req)
        }
        return sync_map

    request: BaseRequest = sync_rec.request
    result = None
    if sync_rec.sync_action is ExternalSync.SYNC_ACTION_CREATE_ACCOUNT:
        req: AccountRequest = request
        result = sync_client.idam_jjo_service.create_user(
            req.jjo_login_id, _format_account_map(req))
    elif sync_rec.sync_action is ExternalSync.SYNC_ACTION_AMEND_ACCOUNT:
        req: AccountRequest = request
        result = sync_client.idam_jjo_service.update_user(
            req.jjo_login_id, _format_account_map(req))
    elif sync_rec.sync_action is ExternalSync.SYNC_ACTION_UPSERT_ACCOUNT:
        req: AccountRequest = request
        result = sync_client.idam_jjo_service.update_or_create_user(
            req.jjo_login_id, _format_account_map(req))
    elif sync_rec.sync_action is ExternalSync.SYNC_ACTION_DISABLE_ACCOUNT:
        login_id = request.related_user.jjo_login_id
        if not login_id:
            data = json.loads(sync_rec.sync_data)
            for rec in data:
                if rec['field'] == 'jjo_login_id':
                    login_id = rec['from']
                    break
        if login_id:
            result = sync_client.idam_jjo_service.disable_user(login_id)
    elif sync_rec.sync_action is ExternalSync.SYNC_ACTION_ENABLE_ACCOUNT:
        result = sync_client.idam_jjo_service.enable_user(request.related_user.jjo_login_id)
    if result:
        if result.get('success', False):
            sync_rec.sync_status = ExternalSync.SYNC_STATUS_COMPLETED
            sync_rec.sync_remarks = None
        else:
            sync_rec.sync_status = ExternalSync.SYNC_STATUS_FAILED
            sync_rec.sync_remarks = result.get('remarks', None)
        sync_rec.sync_time = timezone.now()
        sync_rec.save()


def sync_osdp(sync_client: ClusterRpcProxy, sync_rec: ExternalSync):

    def _format_account_map(req: AccountRequest):

        def _format_full_name(request: AccountRequest):
            return ' '.join([rec for rec in [request.dp_last_name, request.dp_first_name] if rec])

        def _format_mail(request: AccountRequest):
            if request.oa_need_lotus_notes:
                if request.ln_internet_address:
                    return '@'.join([request.ln_internet_address, request.ln_mail_domain.name if request.ln_mail_domain else ''])
            return None
        
        (_fullname, hkid) = sync_client.idam_roma_service.get_roma_info(req.dp_roma_id) if req.dp_roma_id else (None, None)
        sync_map = {
            'cn': req.dp_login_id,
            'description': req.post_title,
            'dpdeptid': req.dp_dep_id,
            'dphkid': hkid,
            'dprankcode': req.dp_rank_code.name if req.dp_rank_code else None,
            'dpstaffgroup': req.dp_staff_code.name if req.dp_staff_code else None,
            'employeeType': req.dp_emp_type.name if req.dp_emp_type else None,
            'givenName': req.dp_first_name,
            'sn': req.dp_last_name,
            'fullName': _format_full_name(req),
            'employeeNumber': req.related_user.uam_id if req.related_user else None,
            'inetUserStatus': 'Active',
            'judinetmail': req.dp_net_mail,
            'judnotesid': req.ln_lotus_notes_mail_name,
            'judromaid': req.dp_roma_id,
            # Not sure - "juduid, judnotesid, mail"
            'juduid': req.dp_net_mail,
            'juduserdpp': req.dp_login_id,
            'uid': req.dp_login_id,
            'mail': _format_mail(req)
        }
        return sync_map

    request: BaseRequest = sync_rec.request
    result = None
    if sync_rec.sync_action is ExternalSync.SYNC_ACTION_CREATE_ACCOUNT:
        req: AccountRequest = request
        result = sync_client.idam_osdp_service.create_user(
            req.dp_login_id, _format_account_map(req))
    elif sync_rec.sync_action is ExternalSync.SYNC_ACTION_AMEND_ACCOUNT:
        req: AccountRequest = request
        result = sync_client.idam_osdp_service.update_user(
            req.dp_login_id, _format_account_map(req))
    elif sync_rec.sync_action is ExternalSync.SYNC_ACTION_UPSERT_ACCOUNT:
        req: AccountRequest = request
        result = sync_client.idam_osdp_service.update_or_create_user(
            req.dp_login_id, _format_account_map(req))
    elif sync_rec.sync_action is ExternalSync.SYNC_ACTION_DISABLE_ACCOUNT:
        login_id = request.related_user.dp_login_id
        if not login_id:
            data = json.loads(sync_rec.sync_data)
            for rec in data:
                if rec['field'] == 'dp_login_id':
                    login_id = rec['from']
                    break
        if login_id:
            result = sync_client.idam_osdp_service.disable_user(login_id)
    elif sync_rec.sync_action is ExternalSync.SYNC_ACTION_ENABLE_ACCOUNT:
        result = sync_client.idam_osdp_service.enable_user(request.related_user.dp_login_id)
    if result:
        if result.get('success', False):
            sync_rec.sync_status = ExternalSync.SYNC_STATUS_COMPLETED
            sync_rec.sync_remarks = None
        else:
            sync_rec.sync_status = ExternalSync.SYNC_STATUS_FAILED
            sync_rec.sync_remarks = result.get('remarks', None)
        sync_rec.sync_time = timezone.now()
        sync_rec.save()

## TO BE COMPLETED ##
def sync_ad(sync_client: ClusterRpcProxy, sync_rec: ExternalSync):

    def _format_account_map(req: AccountRequest):

        # def _format_full_name(request: AccountRequest):
        #     return ' '.join([rec for rec in [request.dp_last_name, request.dp_first_name] if rec])

        def _format_mail(request: AccountRequest):
            if request.oa_need_lotus_notes:
                if request.ln_internet_address:
                    return '@'.join([request.ln_internet_address, request.ln_mail_domain.name if request.ln_mail_domain else ''])
            return None
        
        sync_map = {
            'cn': req.ad_windows_login_name,
            'password': req.ad_windows_login_password,
            'accountExpires': req.ad_account_expiry_date,
            'displayName': req.ad_windows_login_name,
            'givenName': req.ad_windows_first_name,
            'name': req.ad_windows_login_name,
            'mail': _format_mail(req),
            'givenName': req.dp_first_name,
            'sn': req.dp_last_name,
            'fullName': _format_mail(req),
            'sAMAccountName': req.ad_windows_login_name,
            'userPrincipalName': req.ad_windows_login_name,
            'sn': req.ad_windows_last_name,
        }
        return sync_map

    request: BaseRequest = sync_rec.request
    result = None
    if sync_rec.sync_action is ExternalSync.SYNC_ACTION_CREATE_ACCOUNT:
        req: AccountRequest = request
        result = sync_client.idam_osdp_service.create_user(
            req.dp_login_id, _format_account_map(req))
    elif sync_rec.sync_action is ExternalSync.SYNC_ACTION_AMEND_ACCOUNT:
        req: AccountRequest = request
        result = sync_client.idam_osdp_service.update_user(
            req.dp_login_id, _format_account_map(req))
    elif sync_rec.sync_action is ExternalSync.SYNC_ACTION_UPSERT_ACCOUNT:
        req: AccountRequest = request
        result = sync_client.idam_osdp_service.update_or_create_user(
            req.dp_login_id, _format_account_map(req))
    elif sync_rec.sync_action is ExternalSync.SYNC_ACTION_DISABLE_ACCOUNT:
        login_id = request.related_user.dp_login_id
        if not login_id:
            data = json.loads(sync_rec.sync_data)
            for rec in data:
                if rec['field'] == 'dp_login_id':
                    login_id = rec['from']
                    break
        if login_id:
            result = sync_client.idam_osdp_service.disable_user(login_id)
    elif sync_rec.sync_action is ExternalSync.SYNC_ACTION_ENABLE_ACCOUNT:
        result = sync_client.idam_osdp_service.enable_user(request.related_user.dp_login_id)
    if result:
        if result.get('success', False):
            sync_rec.sync_status = ExternalSync.SYNC_STATUS_COMPLETED
            sync_rec.sync_remarks = None
        else:
            sync_rec.sync_status = ExternalSync.SYNC_STATUS_FAILED
            sync_rec.sync_remarks = result.get('remarks', None)
        sync_rec.sync_time = timezone.now()
        sync_rec.save()

def sync_interface(client: ClusterRpcProxy, sync_rec: ExternalSync):
    if sync_rec.sync_type is ExternalSync.SYNC_JJO_PORTAL:
        sync_jjo(client, sync_rec)
    elif sync_rec.sync_type is ExternalSync.SYNC_DEPT_PORTAL:
        sync_osdp(client, sync_rec)
