from nameko.standalone.rpc import ClusterRpcProxy
from django.conf import settings

from rest_framework import serializers
from rest_framework.generics import GenericAPIView
from django.utils import timezone
from common.jud_auth import SAML_SESSION_UAM_ID
from uam_users.models import UamUser
from codetables.models import SectionRelatedMixin
from rest_framework.filters import BaseFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator
from django.utils.functional import cached_property

# from django_nameko import get_pool
# DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"
# DATE_FORMAT = "%d/%m/%Y"

import logging


class DateTimeFieldWithTZ(serializers.DateTimeField):
    def to_representation(self, value):
        value = timezone.localtime(value)
        return super(DateTimeFieldWithTZ, self).to_representation(value)


def get_common_nameko_client():
    config = {'AMQP_URI': settings.AMQP_URI, 'AMQP_SSL': settings.AMQP_SSL}
    return ClusterRpcProxy(config, timeout=5)


def get_nameko_client_for_audit_log():
    return get_common_nameko_client()
    # config = {'AMQP_URI': settings.AMQP_URI, 'AMQP_SSL': settings.AMQP_SSL}
    # return ClusterRpcProxy(config, timeout=5)
    # return get_pool().next()


def get_request_log(request_id):
    with get_nameko_client_for_audit_log() as client:
        return client.idam_audit_log_service.get_request_log(request_id)


def get_field_value(instance, data_dict, field_name):
    '''
    Get field with field_name from data_dict if it existed in there,
    Otherwise, return the field from instance
    '''
    return data_dict.get(field_name, getattr(instance, field_name, None))


def compare_value(value1, value2, none_is_open_ended=True):
    '''
    Compare two value
    # Returns:
        1 if value1 > value2
        0 if value1 == value2
        -1 if value1 < value2
        if one of them none, 
            if none_is_open_ended is True,
                if both value1 and value2 is none -> 0
                else return -1 since the none side is open ended
            else:
                if both value1 and value2 is none -> 0
                else, the non-none value will be larger (e.g. if value1 is not none, 1, else -1)
    '''
    if value1 == value2:
        return 0
    if value1 is not None and value2 is not None:
        return 1 if value1 > value2 else -1
    if none_is_open_ended:
        return -1
    else:
        return -1 if value1 is None else 1


class SectionFilterBackend(BaseFilterBackend):
    '''
    A mixin for Django Rest Framework View to limit current user to access information according to his/her right
    '''

    logger = logging.getLogger(__name__)

    def filter_queryset(self, request, queryset, view):
        if 'uam_requests.can_manage_all_sections' in request.user.get_all_permissions():
            '''
            No need to scope the section information if the current user can manage all sections
            '''
            return queryset
        else:
            uid = request.session.get(SAML_SESSION_UAM_ID, None)
            if uid:
                uid = int(uid)
                try:
                    uam_user = UamUser.objects.select_related(
                        'section').get(uam_id=uid)
                    self.logger.debug('Current UAM User: %s of section: %s' % (
                        uam_user.ad_windows_login_name, uam_user.section))
                    queryset = queryset.filter(section=uam_user.section)
                    return queryset
                except UamUser.DoesNotExist:
                    self.logger.warn(
                        'Current User with UAM_ID %s does not exist.  Thus, empty queryset will be returned' % uid)
                    return queryset.none()
        return queryset.none()


class JudPageNumberPagination(PageNumberPagination):
    class _CustomPaginatorClass(Paginator):
        @cached_property
        def count(self):
            return self.object_list.values('id').count()
    django_paginator_class = _CustomPaginatorClass
    page_size_query_param = 'rows'
    page_size = 10
    max_page_size = 100
