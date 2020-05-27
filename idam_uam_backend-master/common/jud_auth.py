import logging
from urllib.parse import urlparse
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import HttpResponseRedirect, JsonResponse
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from onelogin.saml2.auth import OneLogin_Saml2_Auth, OneLogin_Saml2_Settings
from rest_framework.authentication import BaseAuthentication, SessionAuthentication
from rest_framework.exceptions import NotAuthenticated
from uam_users.models import UamUser

SAML_SESSION_USER_ID = 'session_user_id'
SAML_SESSION_UAM_ID = 'session_uam_id'
SAML_SESSION_USER_SECTION = 'session_user_section'

LOGGER = logging.getLogger(__name__)


class JudSAMLBackend(ModelBackend):
    def authenticate(self, request, **kwargs):
        id = request.session.get(SAML_SESSION_USER_ID, None)
        return self.get_user(id) if id is not None else None


def _prepare_saml_auth(request):
    saml_setting = OneLogin_Saml2_Settings(
        custom_base_path=settings.SAML_FOLDER)
    metadata = saml_setting.get_sp_data()
    saml_server_url = metadata['assertionConsumerService']['url']
    parsed_saml_server_url = urlparse(saml_server_url)
    req = {
        'https': 'on' if parsed_saml_server_url.scheme == 'https' else 'off',
        'http_host': parsed_saml_server_url.hostname,
        'script_name': parsed_saml_server_url.path.split('/')[0],
        'server_port': parsed_saml_server_url.port,
        'get_data': request.GET.copy(),
        'lowercase_urlencoding': True,
        'post_data': request.POST.copy(),
    }
    auth = OneLogin_Saml2_Auth(req, custom_base_path=settings.SAML_FOLDER)
    return auth


def _login(request, attributes):
    user_name = attributes.get('username', None)
    uid = attributes.get('uid', None)
    if user_name and len(user_name) > 0:
        try:
            user = User.objects.get(username__iexact=user_name[0])
            login(request, user, backend='%s.%s' %
                  (JudSAMLBackend.__module__, JudSAMLBackend.__name__))
        except User.DoesNotExist:
            user = User.objects.create_user(username=user_name[0])
        request.session[SAML_SESSION_USER_ID] = user.id if user else None
    if uid and len(uid) > 0:
        request.session[SAML_SESSION_UAM_ID] = uid[0]
        try:
            uam_user = UamUser.objects.select_related(
                'section').get(uam_id=uid[0])
            if uam_user.section:
                tmp_dict = model_to_dict(uam_user.section)
                tmp_dict['display_text'] = '%s: %s' % (
                    uam_user.section.code, uam_user.section.description)
                request.session[SAML_SESSION_USER_SECTION] = tmp_dict
            else:
                LOGGER.warning('User: %s with uam_id %s does not have section defined' % (
                    user_name[0], uid[0]))
        except UamUser.DoesNotExist:
            LOGGER.warning('User: %s with uam_id %s not found' %
                           (user_name[0], uid[0]))


def single_sign_on(request):
    if request.user.is_anonymous:
        auth = _prepare_saml_auth(request)
        return HttpResponseRedirect(auth.login())
    else:
        return HttpResponseRedirect('/')


@csrf_exempt
def single_sign_on_success(request):
    auth = _prepare_saml_auth(request)
    auth.process_response()
    _login(request, auth.get_attributes())
    return HttpResponseRedirect('/')


def get_current_user_info(request):
    # print(request.user, request.session.get(SAML_SESSION_USER_ID, None))
    if request.user.is_anonymous:
        to_return = {
            'username': None,
            'permissions': [],
            'section': None,
            'uam_id': None,
        }
    else:
        to_return = {
            'username': request.user.username,
            'permissions': [permission for permission in request.user.get_all_permissions() if permission.startswith('uam_requests.can_')],
            'section': request.session.get(SAML_SESSION_USER_SECTION, None),
            'uam_id': request.session.get(SAML_SESSION_UAM_ID, None),
        }
    return JsonResponse(to_return)


class JudAuthentication(SessionAuthentication):

    def authenticate_header(self, request):
        return 'Session'
