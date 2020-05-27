# from winreg import QueryValue
from django.db import models
from django.db.models import Case, Value, When
from rest_framework import viewsets, mixins
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from uam_requests.permissions import CanEnquireAccount
from uam_requests.models import BaseRequest
from common import utils, exceptions
from .models import UamUser
from .serializers import UamUserSerializer, UamUserListSerializer


class UamUserView(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = UamUser.objects.all()
    #     .select_related('substantive_rank').select_related('ad_ou')
    permission_classes = (CanEnquireAccount, )
    serializer_class = UamUserSerializer

    def get_queryset(self):
        qs = self.queryset
        foreign_keys = ['section', 'master_rank',
                        'substantive_rank', 'ad_ou', ]
        for key in foreign_keys:
            qs = qs.select_related(key)
        return qs

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        param = self.request.query_params
        if pk:
            for_update = param.get('for_update', False)
            if for_update:
                account_exist = BaseRequest.objects.filter(related_user__id=pk).filter(
                    status__in=[BaseRequest.STATUS_NEW, BaseRequest.STATUS_PENDING_REVIEW_ITOO,
                                BaseRequest.STATUS_PENDING_REVIEW_ITOT]
                ).count()
                if account_exist:
                    raise exceptions.UserBeingUpdated()
        return super().retrieve(request, *args, **kwargs)


class UamUserListView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = UamUser.objects.select_related(
        'section').all().order_by('uam_id')
    filter_backends = (OrderingFilter, utils.SectionFilterBackend,)
    serializer_class = UamUserListSerializer
    permission_classes = (CanEnquireAccount, )
    pagination_class = utils.JudPageNumberPagination
    ordering_fields = ['uam_id', 'surname', 'given_name', 'account_status_name', 'ad_windows_login_name',
                       'ln_lotus_notes_mail_name', 'post_title', 'section']

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(
            account_status_name=Case(
                *[When(account_status=k, then=Value(v))
                  for k, v in UamUser.ACCOUNT_STATUS],
                default=Value('Others'),
                output_field=models.CharField(),
            )
        )
        param = self.request.query_params
        for_update = param.get('for_update', None)
        if for_update:
            qs = qs.exclude(requests__status__in=[BaseRequest.STATUS_NEW, BaseRequest.STATUS_PENDING_REVIEW_ITOO,
                                                  BaseRequest.STATUS_PENDING_REVIEW_ITOT])
        uam_id = param.get('uam_id', None)
        if uam_id:
            qs = qs.filter(uam_id__contains=uam_id)
        surname = param.get('surname', None)
        if surname:
            name_list = surname.split()
            for name in name_list:
                qs = qs.filter(surname__icontains=name)
        given_name = param.get('givenname', None)
        if given_name:
            name_list = given_name.split()
            for name in name_list:
                qs = qs.filter(given_name__icontains=name)
        ad_windows_login_name = param.get('win_login_name')
        if ad_windows_login_name:
            name_list = ad_windows_login_name.split()
            for name in name_list:
                qs = qs.filter(ad_windows_login_name__icontains=name)
        ln_lotus_notes_mail_name = param.get('notes_mail')
        if ln_lotus_notes_mail_name:
            name_list = ln_lotus_notes_mail_name.split()
            for name in name_list:
                qs = qs.filter(ln_lotus_notes_mail_name__icontains=name)
        # account_type??
        account_status = param.get('account_status')
        if account_status:
            qs = qs.filter(account_status=account_status)
        post_title = param.get('post_title')
        if post_title:
            name_list = post_title.split()
            for name in name_list:
                qs = qs.filter(post_title__icontains=name)
        section = param.get('section')
        if section:
            qs = qs.filter(section=section)
        account_type = param.get('account_type', None)
        if account_type:
            qs = qs.filter(account_type=account_type)
        qs = qs.values(
            'id', 'uam_id', 'surname', 'given_name', 'ad_windows_login_name', 'ln_lotus_notes_mail_name',
            'post_title', 'section__id', 'section__code', 'account_status_name', 'account_status',
        )
        return qs


class UserEmailList(viewsets.ViewSet):
    queryset = UamUser.objects.all()

    def list(self, request, *args, **kwargs):
        mail_name = request.query_params.get('mail_name', None)
        # print(request.query_params)
        if mail_name is not None:
            for mail in mail_name.split():
                self.queryset = self.queryset.filter(
                    ln_lotus_notes_mail_name__icontains=mail)
        else:
            self.queryset = self.queryset.filter(
                ln_lotus_notes_mail_name__isnull=False)
        self.queryset = self.queryset.values('ln_lotus_notes_mail_name').distinct().order_by(
            'ln_lotus_notes_mail_name')[:30]
        # print(self.queryset)
        # return super(UserEmailList, self).list(request, *args, **kwargs)
        return Response([{'email': data['ln_lotus_notes_mail_name']} for data in self.queryset])


class AdNameList(viewsets.ViewSet):
    queryset = UamUser.objects.all()

    def list(self, request):
        name_str = request.query_params.get('name', None)
        if name_str:
            for name in name_str.split():
                self.queryset = self.queryset.filter(
                    ad_windows_login_name__icontains=name)
        else:
            self.queryset = self.queryset.filter(
                ad_windows_login_name__isnull=False)
        self.queryset = self.queryset.values(
            'ad_windows_login_name').distinct().order_by('ad_windows_login_name')[:30]
        return Response([data for data in self.queryset])
