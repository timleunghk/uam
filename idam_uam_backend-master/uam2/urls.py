"""uam2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from uam_requests import views as request_views
from uam_users import views as uam_users_views
from codetables import views as code_views
from common.jud_auth import single_sign_on, single_sign_on_success, get_current_user_info
from interface import views as interface_views

router = routers.DefaultRouter()
router.register(r'create_account_requests/prepare', request_views.CreateAccountRequestViewSetForSubmit,
                base_name='create_account_request_for_submit')
router.register(r'create_account_requests/review',
                request_views.CreateAccountRequestViewSetForReview, base_name='create_account_requests/review')
router.register(r'create_account_requests/execute',
                request_views.CreateAccountRequestViewSetForExecute, base_name='create_account_requests/execute')
router.register(r'create_account_requests/setupcomp',
                request_views.CreateAccountRequestViewSetForSetpUpComplete, base_name='create_account_requests/setupcomp')
router.register(r'create_account_requests/userack',
                request_views.CreateAccountRequestViewSetForUserAck, base_name='create_account_requests/userack')
router.register(r'reset_pwd_requests',
                request_views.ResetPasswordRequestViewSet, base_name='reset_pwd_requests')
# router.register(r'requests', request_views.BaseRequestList, base_name='requests')
router.register(r'requests', request_views.GenericRequest)
router.register(r'requests', request_views.GenericListRequests)
# router.register(r'users_account', uam_users_views.BaseRequestList, base_name='users_account')
router.register(r'users_account', uam_users_views.UamUserListView)
router.register(r'users_account', uam_users_views.UamUserView)

router.register(r'update_account_requests/prepare', request_views.UpdateAccountRequestViewSetForSubmit,
                base_name='update_account_request_for_submit')
router.register(r'update_account_requests/review',
                request_views.UpdateAccountRequestViewSetForReview, base_name='update_account_requests/review')
router.register(r'update_account_requests/execute',
                request_views.UpdateAccountRequestViewSetForExecute, base_name='update_account_requests/execute')
router.register(r'users_account_disable',
                request_views.DisableAccountRequestViewSet, base_name='users_account_disable')
router.register(r'users_account_enable',
                request_views.EnableAccountRequestViewSet, base_name='users_account_enable')
router.register(r'users_account_delete',
                request_views.DeleteAccountRequestViewSet, base_name='users_account_delete')

# router.register(r'requests_todolist', request_views.ToDoListRequestList, base_name='requests_todolist')

# router.register(r'titles',code_views.TitleView)
# router.register(r'accounttype',code_views.AccountTypeView)
router.register(r'section', code_views.SectionListView)
router.register(r'rank', code_views.MasterRankListView)
router.register(r'adgroups', code_views.AdGroupListView)
router.register(r'lngroups', code_views.LnGroupListView)
router.register(r'adou', code_views.ActiveDirectoryOUListView)
router.register(r'mailaddrs', uam_users_views.UserEmailList)
router.register(r'adnames', uam_users_views.AdNameList)
router.register(r'ln_acc_types', code_views.LnAccountTypeListView)
router.register(r'ln_client_licenses', code_views.LnClientLicenseListView)
router.register(r'ln_mps_ranges', code_views.LnMPSRangeListView)
router.register(r'ln_mail_templates', code_views.LnMailTemplateListView)
router.register(r'ln_mail_file_owners', code_views.LnMailFileOwnerListView)
router.register(r'ln_mail_servers', code_views.LnMailServerListView)
router.register(r'ln_mail_systems', code_views.LnMailSystemListView)
router.register(r'ln_license_types', code_views.LnLicenseTypeListView)
router.register(r'ln_mail_domains', code_views.LnAddressDomainListView)
router.register(r'dp_emp_types', code_views.DpEmployeeTypeListView)
router.register(r'dp_staff_codes', code_views.DpStaffGroupListView)
router.register(r'dp_rank_codes', code_views.DpRankCodeListView)
router.register(r'roma', interface_views.RomaViewSet, basename='roma')
router.register(r'sync', interface_views.ExternalSyncViewSet)

urlpatterns = [
    # url(r'^$', request_views.index),
    path('admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^audit_log/request/(?P<request_id>.+)/$',
        request_views.get_request_audit_log),
    url(r'^upload/request/(?P<request_id>.+)/$',
        request_views.RequestFileView.as_view()),
    url(r'^docs/', include_docs_urls(title='IdAM - UAM Proxy API')),
    url(r'^auth/sso/', single_sign_on, name='sso'),
    url(r'^auth/acs/', single_sign_on_success, name='acs'),
    url(r'^auth/user_info/', get_current_user_info, name='user_info')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
