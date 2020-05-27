'''
Uam Users Model module
'''
import json
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from common.models import AbstractBaseModel
from codetables.models import (
    SectionRelatedMixin, AdGroup, LnGroup, MasterRank, ActiveDirectoryOU, LnAccountType, LnClientLicense,
    LnMPSRange, LnMailFileOwner, LnMailServer, LnMailSystem, LnMailTemplate, LnLicenseType, LnAddressDomain,
    DpEmployeeType, DpRankCode, DpStaffGroup,
)


class CloneableModel(models.Model):
    ''' Base class to clone attributes values from self model to another objects using clone_to method.'''
    class Meta:
        abstract = True

    def clone_to(self, another_instance):
        ''' Clone from self model to another_instance '''
        assert another_instance is not None
        for field in self.get_clone_field_list():
            if hasattr(self, field):
                if isinstance(self.__class__._meta.get_field(field), models.ManyToManyField):
                    if another_instance.id and hasattr(another_instance, field):
                        getattr(another_instance, field).set(
                            getattr(self, field).all())
                elif hasattr(another_instance, field):
                    setattr(another_instance, field, getattr(self, field))

    def compare_fields(self, another_instance, field_list=None):
        """ Compare fields between self and another_instance
            Args:
                another_instance: Another object to be compared
                field_list: List of field names to be compared. If None, the list will be self.get_clone_field_list()
            Return:
                bool: True if all fields are equal, otherwise False
        """
        field_list = self.get_clone_field_list() if field_list is None else field_list
        for field in field_list:
            if hasattr(self, field) and hasattr(another_instance, field):
                if getattr(self, field) != getattr(another_instance, field):
                    return False
            else:
                return False
        return True

    def get_clone_field_list(self):
        ''' List of string (i.e. field names) to be cloned.  Default to empty -> no fields will be cloned '''
        return []

# Create your models here.


class AbstractUamUser(CloneableModel, AbstractBaseModel, SectionRelatedMixin):
    '''
    Abstract Uam User model.
    Known child: UamUser, CreateAccountRequest and UamAccountRequest
    '''
    STATUS_ACTIVE = 0
    STATUS_DISABLED = 1
    STATUS_DELETED = 2
    ACCOUNT_STATUS = (
        (STATUS_ACTIVE, 'Active'),
        (STATUS_DISABLED, 'Disabled'),
        (STATUS_DELETED, 'Deleted'),
    )
    TITLE_MR = 'Mr.'
    TITLE_MS = 'Ms.'
    TITLE_MRS = 'Mrs.'
    TITLE_DR = 'Dr.'
    TITLE_CHOICES = (
        (TITLE_MR, TITLE_MR),
        (TITLE_MS, TITLE_MS),
        (TITLE_MRS, TITLE_MRS),
        (TITLE_DR, TITLE_DR),
    )

    ACCOUNT_TYPE_NON_JJO = 2
    ACCOUNT_TYPE_JJO = 1
    ACCOUNT_TYPE_SPECIAL = 3
    ACCOUNT_TYPES = (
        (ACCOUNT_TYPE_JJO, 'JJO'),
        (ACCOUNT_TYPE_NON_JJO, 'Non-JJO'),
        (ACCOUNT_TYPE_SPECIAL, 'Special Account'),
    )
    account_effective_start_date = models.DateField(
        blank=True, null=True, help_text='Account Effective Start Date')
    account_effective_end_date = models.DateField(
        blank=True, null=True, help_text='Account Effective End Date')
    # title = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length=6, blank=True,
                             null=True, help_text='Title')
    surname = models.CharField(
        max_length=50, blank=True, null=True, help_text='Surname')
    given_name = models.CharField(
        max_length=100, blank=True, null=True, help_text='Given Name')
    surname_chinese = models.CharField(
        max_length=50, blank=True, null=True, help_text='Surname (Chinese)')
    given_name_chinese = models.CharField(
        max_length=100, blank=True, null=True, help_text='Given Name (Chinese)')
    prefered_name = models.CharField(
        max_length=100, blank=True, null=True, help_text='Prefered Name')
    post_title = models.CharField(
        max_length=100, blank=True, null=True, help_text='Post Title')
    account_type = models.IntegerField(
        default=ACCOUNT_TYPE_NON_JJO, choices=ACCOUNT_TYPES, help_text="Account type")

    oa_need_windows_login = models.BooleanField(
        default=False, help_text='Required Windows Account?')
    oa_need_lotus_notes = models.BooleanField(
        default=False, help_text='Required Notes Account?')
    oa_need_jjo = models.BooleanField(
        default=False, help_text='Required JJO Portal Account?')
    oa_need_dp = models.BooleanField(
        default=False, help_text='Required Departmental Portal Account?')
    account_status = models.IntegerField(
        default=STATUS_ACTIVE, choices=ACCOUNT_STATUS, help_text='Account Status')

    ad_user_groups = models.ManyToManyField(AdGroup)
    ad_windows_login_name = models.CharField(
        max_length=255, blank=True, null=True, help_text='Windows Account Login Name')
    ad_account_expiry_date = models.DateField(
        blank=True, null=True, help_text='Windows Account Expiry Date')
    ad_need_change_password_next_login = models.BooleanField(
        default=True, help_text='User needs to change password at next login?')
    ad_windows_login_password = models.CharField(
        max_length=255, blank=True, null=True, help_text='Windows Account Login Password')
    ad_is_magistrate_of_lt = models.BooleanField(
        default=False, help_text='Magistrate/Presiding Officer of Labour Tribunal')

    _ad_ps_magistrate_of_lt = models.CharField(
        max_length=1000, blank=True, null=True, help_text='PS of Magistrate/Presiding Officer of Labour Tribunal', db_column='ad_ps_magistrate_of_lt')

    def get_ad_ps_magistrate_of_lt(self):
        if self._ad_ps_magistrate_of_lt:
            return json.loads(self._ad_ps_magistrate_of_lt)
        return []

    def set_ad_ps_magistrate_of_lt(self, value):
        if value:
            self._ad_ps_magistrate_of_lt = json.dumps(value)
        else:
            self._ad_ps_magistrate_of_lt = json.dumps([])

    ad_ps_magistrate_of_lt = property(
        get_ad_ps_magistrate_of_lt, set_ad_ps_magistrate_of_lt)

    ad_windows_first_name = models.CharField(
        max_length=255, blank=True, null=True, help_text='Windows First Name')
    ad_windows_last_name = models.CharField(
        max_length=255, blank=True, null=True, help_text='Windows Last Name')

    ln_lotus_notes_mail_name = models.CharField(
        max_length=50, blank=True, null=True, help_text='Notes Account Mail Name')
    ln_short_name = models.CharField(
        max_length=50, blank=True, null=True, help_text='Notes Account Short Name')
    ln_middle_name = models.CharField(
        max_length=50, blank=True, null=True, help_text='Notes Account Middle Name')
    ln_first_name = models.CharField(
        max_length=50, blank=True, null=True, help_text='Notes Account First Name')
    ln_last_name = models.CharField(
        max_length=50, blank=True, null=True, help_text='Notes Account Last Name')
    ln_notes_display_name = models.CharField(
        max_length=50, blank=True, null=True, help_text='Notes Account Display Name')
    ln_notes_account = models.CharField(
        max_length=50, blank=True, null=True, help_text='Notes Account Name')
    ln_notes_password = models.CharField(
        max_length=50, blank=True, null=True, help_text='Notes Password')
    ln_is_internet_mail_user = models.BooleanField(
        default=False, help_text='Internet Mail User?')
    ln_is_gcn_user = models.BooleanField(
        default=False, help_text='GCN User?')
    ln_is_inote_user = models.BooleanField(
        default=False, help_text='iNote User?')
    ln_is_confidential_mail_user = models.BooleanField(
        default=False, help_text='Confidential Mail User?')
    ln_is_contractor = models.BooleanField(
        default=False, help_text='Contractor?')
    ln_user_groups = models.ManyToManyField(LnGroup)
    ln_mail_file_name = models.CharField(
        max_length=255, blank=True, null=True, help_text='Mail File Name')
    ln_set_database_quota = models.BooleanField(
        default=False, help_text="Set Database Quota?")
    ln_database_quota = models.IntegerField(
        null=True, help_text="Database Quota (MB)")
    ln_set_warning_threshold = models.BooleanField(
        default=False, help_text="Set Warning Threshold?")
    ln_warning_threshold = models.IntegerField(
        null=True, help_text="Warning Threshold (MB)")
    ln_remarks = models.TextField(null=True)
    ln_internet_address = models.SlugField(null=True, max_length=255)

    jjo_login_id = models.CharField(
        max_length=255, blank=True, null=True, help_text='JJ Portal Login ID')
    jjo_email = models.SlugField(
        null=True, max_length=255, help_text='JJO Portal email address')
    jjo_first_name = models.CharField(
        max_length=50, blank=True, null=True, help_text='JJO Portal First Name')
    jjo_last_name = models.CharField(
        max_length=50, blank=True, null=True, help_text='JJO Portal Last Name')

    dp_login_id = models.CharField(
        max_length=255, blank=True, null=True, help_text='DP Login ID')
    dp_dep_id = models.CharField(
        max_length=50, blank=True, null=True, help_text='Department ID')
    dp_uid_saml = models.CharField(
        max_length=50, blank=True, null=True, help_text='Unique ID for SAML')
    dp_net_mail = models.CharField(
        max_length=255, blank=True, null=True, help_text='Net Mail Address')
    dp_first_name = models.CharField(
        max_length=50, blank=True, null=True, help_text='DP First Name')
    dp_last_name = models.CharField(
        max_length=50, blank=True, null=True, help_text='DP Last Name')
    dp_roma_id = models.SlugField(
        max_length=50, blank=True, null=True, help_text='ROMA ID')
    dp_roma_full_name = models.CharField(
        max_length=255, blank=True, null=True, help_text='ROMA Full Name')
    dp_hkid = models.SlugField(
        max_length=10, blank=True, null=True, help_text='HKID (First 4 letters)')

    def get_clone_field_list(self):
        return ['account_effective_start_date', 'account_effective_end_date', 'title', 'surname', 'given_name', 'post_title',
                'oa_need_windows_login', 'oa_need_lotus_notes', 'oa_need_jjo', 'oa_need_dp',
                'surname_chinese', 'given_name_chinese', 'prefered_name',
                'ad_windows_login_name', 'ad_account_expiry_date', 'ad_need_change_password_next_login', 'ad_windows_login_password',
                'ad_is_magistrate_of_lt', '_ad_ps_magistrate_of_lt', 'ad_windows_first_name', 'ad_windows_last_name',
                'ln_lotus_notes_mail_name', 'ln_short_name', 'ln_notes_display_name', 'ln_notes_account', 'ln_notes_password', 'section',
                'ln_middle_name', 'ln_first_name', 'ln_last_name',
                'ln_account_type', 'ln_client_license',
                'ln_mps_range', 'ln_mail_system', 'ln_mail_file_owner', 'ln_mail_template', 'ln_mail_server', 'ln_license_type',
                'ln_is_internet_mail_user', 'ln_is_gcn_user', 'ln_is_inote_user', 'ln_is_confidential_mail_user', 'ln_is_contractor',
                'ln_mail_file_name', 'ln_set_database_quota', 'ln_database_quota', 'ln_set_warning_threshold', 'ln_warning_threshold',
                'ln_remarks', 'ln_internet_address', 'ln_mail_domain',
                'account_type', 'ad_user_groups', 'section', 'ln_user_groups', 'master_rank', 'substantive_rank', 'ad_ou',
                'jjo_login_id', 'jjo_email', 'jjo_mail_domain', 'jjo_first_name', 'jjo_last_name', 'jjo_emp_type',
                'dp_login_id', 'dp_dep_id', 'dp_uid_saml', 'dp_net_mail', 'dp_first_name', 'dp_last_name', 'dp_roma_id', 'dp_roma_full_name',
                'dp_hkid', 'dp_emp_type', 'dp_rank_code', 'dp_staff_code',
                ]

    class Meta:
        abstract = True


class UamUser(AbstractUamUser):
    '''
    UamUser Model holding the all UamUser records
    '''
    uam_id = models.IntegerField(unique=True, null=True)
    ad_sync_time = models.DateTimeField(null=True)
    notes_sync_time = models.DateTimeField(null=True)

    master_rank = models.ForeignKey(
        MasterRank, on_delete=models.PROTECT, null=True, related_name='master_ranked_user')
    substantive_rank = models.ForeignKey(
        MasterRank, on_delete=models.PROTECT, null=True, related_name='substantive_ranked_user')
    ad_ou = models.ForeignKey(
        ActiveDirectoryOU, on_delete=models.PROTECT, null=True, related_name='ad_ou_user')
    ln_account_type = models.ForeignKey(
        LnAccountType, on_delete=models.PROTECT, null=True, related_name='ln_account_type_user')
    ln_client_license = models.ForeignKey(
        LnClientLicense, on_delete=models.PROTECT, null=True, related_name='ln_client_license_user')
    ln_mps_range = models.ForeignKey(
        LnMPSRange, on_delete=models.PROTECT, null=True, related_name='ln_mps_range_user')
    ln_mail_system = models.ForeignKey(
        LnMailSystem, on_delete=models.PROTECT, null=True, related_name='ln_mail_system_user')
    ln_mail_file_owner = models.ForeignKey(
        LnMailFileOwner, on_delete=models.PROTECT, null=True, related_name='ln_mail_file_owner_user')
    ln_mail_template = models.ForeignKey(
        LnMailTemplate, on_delete=models.PROTECT, null=True, related_name='ln_mail_template_user')
    ln_mail_server = models.ForeignKey(
        LnMailServer, on_delete=models.PROTECT, null=True, related_name='ln_mail_server_user')
    ln_license_type = models.ForeignKey(
        LnLicenseType, on_delete=models.PROTECT, null=True, related_name='ln_license_type_user')
    ln_mail_domain = models.ForeignKey(
        LnAddressDomain, on_delete=models.PROTECT, null=True, related_name='ln_mail_domain_user')
    jjo_mail_domain = models.ForeignKey(
        LnAddressDomain, on_delete=models.PROTECT, null=True, related_name='jjo_mail_domain_user')
    dp_emp_type = models.ForeignKey(
        DpEmployeeType, on_delete=models.PROTECT, null=True, related_name='dp_emp_type_user')
    dp_rank_code = models.ForeignKey(
        DpRankCode, on_delete=models.PROTECT, null=True, related_name='dp_rank_code_user')
    dp_staff_code = models.ForeignKey(
        DpStaffGroup, on_delete=models.PROTECT, null=True, related_name='dp_staff_code_user')
    jjo_emp_type = models.ForeignKey(
        DpEmployeeType, on_delete=models.PROTECT, null=True, related_name='jjo_emp_type_user')

@receiver(post_save, sender=UamUser)
def set_uam_id(sender, instance, **_kwargs):
    '''
    A trigger to generate UAM ID if UAM ID was not generated yet when an UamUser was saved.
    '''
    if not instance.uam_id:
        # instance.uam_id = "%010d" % instance.pk
        instance.uam_id = instance.pk
        instance.save()
