import json
import os
from datetime import datetime
from django.db import models
from django.db.models.signals import post_save
from django.forms.models import model_to_dict
from django.dispatch import receiver
from polymorphic.models import PolymorphicModel
from common.models import AbstractBaseModel
from codetables.models import (
    SectionRelatedMixin, MasterRank, ActiveDirectoryOU, LnAccountType, LnClientLicense, LnMPSRange,
    LnMailSystem, LnMailFileOwner, LnMailTemplate, LnMailServer, LnLicenseType, LnAddressDomain,
    DpEmployeeType, DpRankCode, DpStaffGroup,
)
from uam_users.models import AbstractUamUser, UamUser
# from uam_requests.utils import compare_request_changes


class AuditLog(models.Model):
    audit_log_data = models.TextField(null=False, blank=False)
    log_time = models.DateTimeField(auto_now_add=True)
    sync_time = models.DateTimeField(null=True)

# Create your models here.


class BaseRequest(PolymorphicModel, AbstractBaseModel, SectionRelatedMixin):
    ''' Base Model for all Requests '''
    STATUS_NEW = 0
    STATUS_PENDING_REVIEW_ITOO = 1
    STATUS_PENDING_REVIEW_ITOT = 2
    STATUS_CONFIRMED_BY_HELPDESK = 3
    STATUS_REJECTED_BY_ITOO = 4
    STATUS_REJECTED_BY_ITOT = 5
    STATUS_SETUP_COMPLETED = 6
    STATUS_USER_ACK = 7
    STATUS_RESET_PW_COMPLETED = 8
    STATUS_DISABLE_COMPLETED = 9
    STATUS_ENABLE_COMPLETED = 10
    STATUS_DELETE_COMPLETED = 11
    STATUS_UPDATE_COMPLETED = 12
    STATUS_WITHDRAWN = 13

    REQUEST_STATUSES = (
        (STATUS_NEW, 'New'),
        (STATUS_PENDING_REVIEW_ITOO, 'Pending For ITOO\'s review'),
        (STATUS_PENDING_REVIEW_ITOT, 'Pending For ITOT\'s review'),
        (STATUS_CONFIRMED_BY_HELPDESK, 'Confirmed by HelpDesk'),
        (STATUS_REJECTED_BY_ITOO, 'Rejected by ITOO'),
        (STATUS_REJECTED_BY_ITOT, 'Rejected by ITOT'),
        (STATUS_SETUP_COMPLETED, 'Setup Completed'),
        (STATUS_USER_ACK, 'User Acknowledged'),
        (STATUS_RESET_PW_COMPLETED, 'Reset Password Completed'),
        (STATUS_DISABLE_COMPLETED, 'Disable Account Completed'),
        (STATUS_ENABLE_COMPLETED, 'Re-Enable Account Completed'),
        (STATUS_DELETE_COMPLETED, 'Delete Account Completed'),
        (STATUS_UPDATE_COMPLETED, 'Update Account Completed'),
        (STATUS_WITHDRAWN, 'Withdrawn')
    )

    REQUEST_STATUSES_DICT = dict(REQUEST_STATUSES)

    REQUEST_TYPES_POLYMORPHIC = (
        (16, 'Create Account', 'accountrequest', "createaccountrequest"),
        (17, 'Update Account', 'accountrequest', "updateaccountrequest"),
        (19, 'Delete Account', 'related_user', "deleteaccountrequest"),
        (15, 'Reset Password', 'related_user', "resetpasswordrequest"),
        (18, 'Disable Account', 'related_user', "disableaccountrequest"),
        (110, 'Re-enable Account', 'related_user', "enableaccountrequest"),
    )

    '''
    REQUEST_TYPES = (
        (1, 'Create Account'),
        (2, 'Update Account'),
        (3, 'Delete Account'),
    #   (4, 'Change Password'),
        (5, 'Reset Password'),
        (6, 'Disable Account'),
        (7, 'Re-enable Account'),
    )
    '''

    related_user = models.ForeignKey(
        UamUser, on_delete=models.SET_DEFAULT, default=None, related_name="requests", null=True)
    submission_date = models.DateField(null=True)
    # status = FSMIntegerField(default=STATUS_NEW, choices=REQUEST_STATUSES, protected=True)
    status = models.IntegerField(default=STATUS_NEW, choices=REQUEST_STATUSES)
    request_id = models.CharField(
        max_length=20, unique=True, null=False, blank=False)

    query_status_desc = models.CharField(max_length=100, null=True)
    query_request_type_desc = models.CharField(max_length=100, null=True)
    query_given_name = models.CharField(max_length=100, null=True)
    query_surname = models.CharField(max_length=100, null=True)
    query_post_title = models.CharField(max_length=100, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['query_status_desc']),
            models.Index(fields=['query_request_type_desc']),
            models.Index(fields=['query_given_name']),
            models.Index(fields=['query_surname']),
            models.Index(fields=['query_post_title']),
        ]

    def _set_query_fields(self):
        '''
        Subclass shall implement this method to set those query fields before save
        The query fields are for SQL selection sorting and pagination
        '''
        if self.related_user:
            self.query_given_name = self.related_user.given_name
            self.query_surname = self.related_user.surname
            self.query_post_title = self.related_user.post_title
            # if self.section is None:
            #     self.section = self.related_user.section

    def save(self, *args, **kwargs):
        self.query_status_desc = BaseRequest.REQUEST_STATUSES_DICT.get(
            self.status)
        self._set_query_fields()
        super().save(*args, **kwargs)


class ResetPasswordRequest(BaseRequest):
    new_password = models.CharField(max_length=50)

    # @transition(field='status', source=BaseRequest.STATUS_NEW, target=BaseRequest.STATUS_COMPLETED)

    def _set_query_fields(self):
        super()._set_query_fields()
        self.query_request_type_desc = 'Reset Password'

    def reset_password(self):
        self.status = BaseRequest.STATUS_RESET_PW_COMPLETED
        self.related_user.ad_windows_login_password = self.new_password
        self.related_user.save()


class AccountRequest(BaseRequest, AbstractUamUser):
    master_rank = models.ForeignKey(
        MasterRank, on_delete=models.PROTECT, null=True, related_name='master_ranked_request')
    substantive_rank = models.ForeignKey(
        MasterRank, on_delete=models.PROTECT, null=True, related_name='substantive_ranked_request')
    ad_ou = models.ForeignKey(
        ActiveDirectoryOU, on_delete=models.PROTECT, null=True, related_name='ad_ou_request')
    ln_account_type = models.ForeignKey(
        LnAccountType, on_delete=models.PROTECT, null=True, related_name='ln_account_type_request')
    ln_client_license = models.ForeignKey(
        LnClientLicense, on_delete=models.PROTECT, null=True, related_name='ln_client_license_request')
    ln_mps_range = models.ForeignKey(
        LnMPSRange, on_delete=models.PROTECT, null=True, related_name='ln_mps_range_request')
    ln_mail_system = models.ForeignKey(
        LnMailSystem, on_delete=models.PROTECT, null=True, related_name='ln_mail_system_request')
    ln_mail_file_owner = models.ForeignKey(
        LnMailFileOwner, on_delete=models.PROTECT, null=True, related_name='ln_mail_file_owner_request')
    ln_mail_template = models.ForeignKey(
        LnMailTemplate, on_delete=models.PROTECT, null=True, related_name='ln_mail_template_request')
    ln_mail_server = models.ForeignKey(
        LnMailServer, on_delete=models.PROTECT, null=True, related_name='ln_mail_server_request')
    ln_license_type = models.ForeignKey(
        LnLicenseType, on_delete=models.PROTECT, null=True, related_name='ln_license_type_request')
    ln_mail_domain = models.ForeignKey(
        LnAddressDomain, on_delete=models.PROTECT, null=True, related_name='ln_mail_domain_request')
    jjo_mail_domain = models.ForeignKey(
        LnAddressDomain, on_delete=models.PROTECT, null=True, related_name='jjo_mail_domain_request')
    dp_emp_type = models.ForeignKey(
        DpEmployeeType, on_delete=models.PROTECT, null=True, related_name='dp_emp_type_request')
    dp_rank_code = models.ForeignKey(
        DpRankCode, on_delete=models.PROTECT, null=True, related_name='dp_rank_code_request')
    dp_staff_code = models.ForeignKey(
        DpStaffGroup, on_delete=models.PROTECT, null=True, related_name='dp_staff_code_request')
    jjo_emp_type = models.ForeignKey(
        DpEmployeeType, on_delete=models.PROTECT, null=True, related_name='jjo_emp_type_request')


    oth_other_request = models.TextField(
        blank=True, null=True, help_text='Other Requests')
    oth_other_justification = models.TextField(
        blank=True, null=True, help_text='Other Justifications')
    oth_other_remark = models.TextField(
        blank=True, null=True, help_text='Other Remarks')


class CreateAccountRequest(AccountRequest):
    installation_contact_person = models.CharField(
        max_length=50, blank=True, null=True, help_text='Installation Contact Person')
    installation_contact_phone_no = models.CharField(
        max_length=50, blank=True, null=True, help_text='Installation Contact Tel.')

    def withdraw(self):
        self.status = BaseRequest.STATUS_WITHDRAWN

    def submit(self):
        self.submission_date = datetime.now().date()
        self.status = BaseRequest.STATUS_PENDING_REVIEW_ITOO

    def review(self):
        self.status = BaseRequest.STATUS_PENDING_REVIEW_ITOT

    def reject_on_review(self):
        self.status = BaseRequest.STATUS_REJECTED_BY_ITOO

    def execute(self):
        new_user = UamUser()
        self.clone_to(new_user)
        new_user.creation_user = self.last_modification_user
        new_user.last_modification_user = self.last_modification_user
        new_user.save()
        new_user.ad_user_groups.set(self.ad_user_groups.all())
        new_user.ln_user_groups.set(self.ln_user_groups.all())
        self.related_user = new_user
        self.status = BaseRequest.STATUS_CONFIRMED_BY_HELPDESK

    def reject_on_execute(self):
        self.status = BaseRequest.STATUS_REJECTED_BY_ITOT

    def set_up_complete(self):
        self.status = BaseRequest.STATUS_SETUP_COMPLETED

    def user_ack(self):
        self.status = BaseRequest.STATUS_USER_ACK

    def _set_query_fields(self):
        self.query_given_name = self.given_name
        self.query_surname = self.surname
        self.query_post_title = self.post_title
        self.query_request_type_desc = 'Create Account'


class UpdateAccountRequest(AccountRequest):
    user_id = models.CharField(
        max_length=50, blank=True, null=True, help_text='User ID')
    _value_changes = models.TextField(null=True, blank=True, db_column='value_changes')

    def get_value_changes(self):
        if self._value_changes:
            return json.loads(self._value_changes)
        else:
            return []

    def set_value_changes(self, value):
        if value:
            self._value_changes = json.dumps(value)
        else:
            self._value_changes = json.dumps([])

    value_changes = property(get_value_changes, set_value_changes)

    def withdraw(self):
        self.status = BaseRequest.STATUS_WITHDRAWN

    def submit(self):
        self.submission_date = datetime.now().date()
        self.status = BaseRequest.STATUS_PENDING_REVIEW_ITOO
        self.value_changes = compare_request_changes(self.related_user, self)
        # self.related_user.save()

    def review(self):
        self.status = BaseRequest.STATUS_PENDING_REVIEW_ITOT
        self.value_changes = compare_request_changes(self.related_user, self)

    def reject_on_review(self):
        self.status = BaseRequest.STATUS_REJECTED_BY_ITOO

    def execute(self):
        # user_id = self.related_user.id
        # user_dict_new = model_to_dict(self)

        # for key in {'id', 'creation_user', 'last_modification_user', 'related_user', 'submission_date', 'status', 'request_id', 'baserequest_ptr', 'accountrequest_ptr', 'account_status', 'user_id', 'oth_other_request', 'oth_other_justification', 'oth_other_remark', 'value_changes', 'query_status_desc', 'query_request_type_desc', 'query_surname', 'query_given_name', 'query_post_title', 'ad_user_groups', 'ln_user_groups'}:
        #     del user_dict_new[key]

        # user_object = UamUser.objects.filter(pk=user_id)

        # old_user_set = set((user_object.values()[0]).items())
        # new_user_set = set(user_dict_new.items())

        # diff_user_dict = dict(old_user_set ^ new_user_set)
        # diff_user_keys = [key for key, value in diff_user_dict.items() if key in {
        #     'account_effective_start_date', 'account_effective_end_date', 'title', 'surname', 'given_name',
        #     'surname_chinese', 'given_name_chinese', 'preferred_name', 'post_title', 'rank', 'substantive_rank',
        #     'acct_type', 'section', 'account_type',
        # }]

        # old_user_dict = {key: value for key, value in (
        #     user_object.values()[0]).items() if key in diff_user_keys}
        # new_user_dict = {key: value for key,
        #                  value in user_dict_new.items() if key in diff_user_keys}

        # user_dict_changes = {'from': old_user_dict, 'to': new_user_dict}
        # #print (str(user_dict_changes))
        self.value_changes = compare_request_changes(self.related_user, self)
        # user_dict_new['last_modification_user'] = self.last_modification_user
        # # print(user_dict_new)
        # user_object.update(**user_dict_new)
        # user_object[0].ad_user_groups.set(self.ad_user_groups.all())
        # user_object[0].save()
        # self.related_user.update(**user_dict_new)
        # for (key,value) in user_dict_new.items():
        #     setattr(self.related_user, key, value)
        # self.related_user.ad_user_groups.set(self.ad_user_groups.all())
        # self.related_user.save()
        # user_object.last_modification_date = datetime.now().date()
        # user_object.last_modification_user = self.last_modification_user
        self.clone_to(self.related_user)
        self.related_user.last_modification_user = self.last_modification_user
        self.related_user.save()
        # self.related_user.save()
        self.status = BaseRequest.STATUS_UPDATE_COMPLETED

    def reject_on_execute(self):
        self.status = BaseRequest.STATUS_REJECTED_BY_ITOT

    def _set_query_fields(self):
        super()._set_query_fields()
        self.query_request_type_desc = 'Update Account'


class DisableAccountRequest(BaseRequest):
    user_id = models.CharField(max_length=50)

    def disable_account(self):
        self.status = BaseRequest.STATUS_DISABLE_COMPLETED
        self.related_user.account_status = UamUser.STATUS_DISABLED
        self.related_user.save()

    @property
    def user_ids(self):
        return None

    @user_ids.setter
    def user_ids(self, value):
        pass

    def _set_query_fields(self):
        super()._set_query_fields()
        self.query_request_type_desc = 'Disable Account'


class EnableAccountRequest(BaseRequest):
    user_id = models.CharField(max_length=50)

    def enable_account(self):
        self.status = BaseRequest.STATUS_ENABLE_COMPLETED
        self.related_user.account_status = UamUser.STATUS_ACTIVE
        self.related_user.save()

    @property
    def user_ids(self):
        return None

    @user_ids.setter
    def user_ids(self, value):
        pass

    def _set_query_fields(self):
        super()._set_query_fields()
        self.query_request_type_desc = 'Re-enable Account'


class DeleteAccountRequest(BaseRequest):
    user_id = models.CharField(max_length=50)

    def delete_account(self):
        self.status = BaseRequest.STATUS_DELETE_COMPLETED
        self.related_user.account_status = UamUser.STATUS_DELETED
        self.related_user.save()

    @property
    def user_ids(self):
        return None

    @user_ids.setter
    def user_ids(self, value):
        pass

    def _set_query_fields(self):
        super()._set_query_fields()
        self.query_request_type_desc = 'Delete Account'


REQUEST_ID_MAP = {
    CreateAccountRequest: 'CA',
    UpdateAccountRequest: 'UA',
    ResetPasswordRequest: 'RP',
    DisableAccountRequest: 'DA',
    EnableAccountRequest: 'EA',
    DeleteAccountRequest: 'RA',
}


@receiver(post_save, sender=CreateAccountRequest)
@receiver(post_save, sender=UpdateAccountRequest)
@receiver(post_save, sender=ResetPasswordRequest)
@receiver(post_save, sender=DisableAccountRequest)
@receiver(post_save, sender=EnableAccountRequest)
@receiver(post_save, sender=DeleteAccountRequest)
def set_request_id(sender, instance, **_kwargs):
    '''
    Automatically generate a request id when a request is first saved
    '''
    if not instance.request_id:
        instance.request_id = "%s%010d" % (
            REQUEST_ID_MAP.get(sender, ''), instance.pk)
        instance.save()
        # instance.request_id = '%s%s' % (datetime.now().strftime('%y%j-%H%M%S-%f'), ''.join(random.choices(string.ascii_uppercase+string.digits)))


class RequestMailTo(models.Model):
    _to = models.CharField(max_length=2000, null=True, db_column="to")
    _cc = models.CharField(max_length=2000, null=True, db_column="cc")
    status = models.IntegerField(choices=BaseRequest.REQUEST_STATUSES)
    request = models.ForeignKey(
        'BaseRequest', related_name="mail_to", on_delete=models.CASCADE)

    def get_to(self):
        if self._to:
            return json.loads(self._to)
        else:
            return []

    def set_to(self, value):
        if value:
            self._to = json.dumps(value)
        else:
            self._to = json.dumps([])

    to = property(get_to, set_to)

    def get_cc(self):
        if self._cc:
            return json.loads(self._cc)
        else:
            return []

    def set_cc(self, value):
        if value:
            self._cc = json.dumps(value)
        else:
            self._cc = json.dumps([])

    cc = property(get_cc, set_cc)

    class Meta:
        unique_together = ['request', 'status']


class RequestFile(models.Model):
    status = models.IntegerField(choices=BaseRequest.REQUEST_STATUSES)
    request = models.ForeignKey(
        'BaseRequest', related_name="uploaded_file", on_delete=models.CASCADE)

    def get_request_file_name(self, filename):
        return '%s/%s-%s-%s' % ('request_files', self.request.request_id, self.status, filename)
    file = models.FileField()
    file_name = models.CharField(max_length=1000, null=True)

    class Meta:
        unique_together = ['request', 'status', 'file']


@receiver(models.signals.post_delete, sender=RequestFile)
def auto_delete_request_file(sender, instance, **_kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class IdamPermissions(models.Model):
    class Meta:
        managed = False
        permissions = (
            ('can_submit_create_request',
             'Can prepare and submit account creation request'),
            ('can_review_create_request',
             'Can review and reject account creation request'),
            ('can_execute_create_request',
             'Can execute and reject account creation request'),
            ('can_enquire_request', 'Can enquire requests'),
            ('can_submit_update_request',
             'Can prepare and submit account update request'),
            ('can_review_update_request',
             'Can review and reject account update request'),
            ('can_execute_update_request',
             'Can execute and reject account update request'),
            ('can_enquire_account', 'Can enquire UAM accounts'),
            ('can_disable_account', 'Can disable UAM accounts'),
            ('can_delete_account', 'Can delete UAM accounts'),
            ('can_reset_password', 'Can Reset Password'),
            ('can_enable_account', 'Can enable account'),
            ('can_manage_all_sections', 'Can Manage user information for all sections'),
            ('can_complete_create_request',
             'Can Complete Setup account creation request'),
        )

# /******************* (‎◉‿◉) [Start] Updated by Ceci (‎◉‿◉) *******************/


def model_to_dict_2(instance):
    _dict = model_to_dict(instance)
    model = instance._meta.model
    for key, val in _dict.items():
        if val == '' or val == None:
            continue
        field = model._meta.get_field(key)
        # Handle output of DateField and DateTimeField
        if field.get_internal_type() == 'DateTimeField' or field.get_internal_type() == 'DateField':
            _dict[field.name] = val.strftime(
                '%d/%m/%Y %H:%M:%S') if val else ''
        # Handle output of Choice Field
        elif field.choices:
            _dict[field.name] = dict(field.choices)[val]
        # Handle output of any relation field. To serialize ForeignKeyField and ManyToManyField
        elif field.is_relation:
            if field.many_to_many:
                # e.g. 'ad_user_groups' is a many to many relation. Get list of AdGroup instances.
                releated_objects = getattr(instance, field.name).all()
                if len(releated_objects) > 0:
                    # e.g. Get model of 'ad_user_groups' => AdGroup
                    related_model = releated_objects[0]._meta.model
                    # e.g. Get field list of 'AdGroup'. The following fields are not included:
                    # - Not include any ManyToMany field
                    # - Not include ['creation_date','creation_user','last_modification_date','last_modification_user']
                    related_model_fields = list(
                        related_model._meta.get_fields())
                    related_model_fields = [x for x in related_model_fields if not x.many_to_many and x.name not in [
                        'creation_date', 'creation_user', 'last_modification_date', 'last_modification_user']]

                    # e.g. Iterate all AdGroup instances in 'ad_user_groups'
                    _val_list = []
                    for related_obj in releated_objects:
                        _entry = {}
                        for _field in related_model_fields:
                            _entry[_field.name] = getattr(
                                related_obj, _field.name)
                        _val_list.append(_entry)
                    # Serialize ManyToMany Field
                    # _dict[field.name] = json.dumps(_val_list)
                    _dict[field.name] = _val_list
            else:
                if len(field.foreign_related_fields) > 0:
                    # e.g. Section object, MasterRank object
                    related_object = getattr(instance, field.name)
                    # e.g. Section (code, description), MasterRank (value, description)
                    related_field = field.foreign_related_fields[0].name

                    # Format 1
                    #_dict[field.name] = getattr(related_object, related_field)

                    # Format 2
                    # e.g. Section, MasterRank
                    related_model = related_object._meta.model
                    # e.g. Section [code, description], MasterRank [value, description]
                    related_model_fields = list(
                        related_model._meta.get_fields())
                    related_model_fields = [x for x in related_model_fields if not x.is_relation and x.name not in [
                        'creation_date', 'creation_user', 'last_modification_date', 'last_modification_user']]

                    _entry = {}
                    for _field in related_model_fields:
                        if _field.get_internal_type() == 'DateTimeField' or _field.get_internal_type() == 'DateField':
                            _val2 = getattr(related_object, _field.name)
                            _entry[_field.name] = _val2.strftime(
                                '%d/%m/%Y %H:%M:%S') if _val2 else ''
                        elif _field.choices:
                            _val2 = getattr(related_object, _field.name)
                            _entry[_field.name] = dict(_field.choices)[_val2]
                        else:
                            _entry[_field.name] = getattr(
                                related_object, _field.name)
                    # _dict[field.name] = json.dumps(_entry)
                    _dict[field.name] = _entry
    special_field_list = [key for key in _dict if key.startswith('_')]
    print(special_field_list)
    for key in special_field_list:
        if hasattr(instance, key[1:]):
            _dict.pop(key)
            _dict[key[1:]] = getattr(instance, key[1:])
    return _dict


def compare_request_changes(uam_user, account_request) -> str:
    # uam_user = UamUser.objects.filter(pk=user_id).first()
    # # Get the latest UpdateAccountRequest object by related_user_id
    # update_req = UpdateAccountRequest.objects.filter(related_user_id=user_id).latest('request_id')
    # # Convert model instance to dict
    uam_user_dict = model_to_dict_2(uam_user)
    update_req_dict = model_to_dict_2(account_request)
    # Finding common properties of UamUser and UpdateAccountRequest. (Compare by field names)
    common_fields = set(uam_user_dict.keys()).intersection(
        update_req_dict.keys())
    common_fields = [x for x in common_fields if x not in [
        'id', 'creation_user', 'last_modification_user', 'creation_date', 'last_modification_date']]
    # Build a tuple list. e.g. [{'field','uam_user_value','update_req_value'}, {......}]
    changed_values = tuple((field, uam_user_dict[field], update_req_dict[field])
                           for field in common_fields if uam_user_dict[field] != update_req_dict[field])
    # # Create a json
    # user_dict_changes = json.dumps(
    #     [{"field": x[0], "from": x[1], "to": x[2]} for x in changed_values])
    # return user_dict_changes
    return [{"field": x[0], "from": x[1], "to": x[2]} for x in changed_values]

# /******************* (‎◉‿◉) [End] Updated by Ceci (‎◉‿◉) *******************/
