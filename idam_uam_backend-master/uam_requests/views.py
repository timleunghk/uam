# from django.core.paginator import Paginator
import re
from django_filters import rest_framework as filters
from django.db.models import Case, When, Q, F
from django.db import models, transaction
from django.shortcuts import render

from rest_framework import status, viewsets, mixins
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

from common import utils
from .models import (AccountRequest, BaseRequest, CreateAccountRequest, DeleteAccountRequest,
                     DisableAccountRequest, EnableAccountRequest, ResetPasswordRequest, UpdateAccountRequest, RequestFile)
from .serializers import (BaseRequestSerializer, CreateAccountRequestSerializerForExecute, CreateAccountRequestSerializerForReview,
                          CreateAccountRequestSerializerForSetupComplete, CreateAccountRequestSerializerForSubmit, CreateAccountRequestSerializerForUserAck,
                          DeleteAccountRequestSerializer, DisableAccountRequestSerializer, EnableAccountRequestSerializer,
                          ResetPasswordRequestSerializer, UpdateAccountRequestSerializerForSubmit, UpdateAccountRequestSerializerForReview,
                          UpdateAccountRequestSerializerForExecute, BaseRequestListSerializer)
from .serializers import BasicBaseRequestSerializer
from .utils import AbstractRequestViewSet, AllowDraftMixin, AllowDraftOnCreateMixin, AllowRejectMixin
# from django.utils.functional import cached_property
from .permissions import (
    CanSubmitCreateRequest, CanExecuteCreateRequest, CanExecuteUpdateRequest,
    CanReviewCreateRequest, CanReviewUpdateRequest, CanSubmitUpdateRequest, CanEnquireRequest,
    CanDeleteAccount, CanDisableAccount, CanEnableAccount, CanResetPassword, CanCompleteSetupCreateAccount,
)


class RequestFilter(filters.FilterSet):
    request_id = filters.CharFilter(
        field_name='request_id', lookup_expr='icontains')

    class Meta:
        model = BaseRequest
        fields = ['request_id', ]


class UpdateAccountRequestViewSetForSubmit(AbstractRequestViewSet, AllowDraftOnCreateMixin, AllowRejectMixin):
    queryset = UpdateAccountRequest.objects.filter(
        status=UpdateAccountRequest.STATUS_NEW)
    serializer_class = UpdateAccountRequestSerializerForSubmit
    http_method_names = ('post', 'put', 'get')
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RequestFilter
    permission_classes = (CanSubmitUpdateRequest,)


class UpdateAccountRequestViewSetForReview(AbstractRequestViewSet, AllowDraftMixin, AllowRejectMixin):
    queryset = UpdateAccountRequest.objects.filter(
        status=UpdateAccountRequest.STATUS_PENDING_REVIEW_ITOO)
    serializer_class = UpdateAccountRequestSerializerForReview
    http_method_names = ('put', 'get')
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RequestFilter
    permission_classes = (CanReviewUpdateRequest,)


class UpdateAccountRequestViewSetForExecute(AbstractRequestViewSet, AllowDraftMixin, AllowRejectMixin):
    queryset = UpdateAccountRequest.objects.filter(
        status=UpdateAccountRequest.STATUS_PENDING_REVIEW_ITOT)
    serializer_class = UpdateAccountRequestSerializerForExecute
    http_method_names = ('put', 'get')
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RequestFilter
    permission_classes = (CanExecuteUpdateRequest,)


class CreateAccountRequestViewSetForSubmit(AbstractRequestViewSet, AllowDraftOnCreateMixin, AllowRejectMixin):
    queryset = CreateAccountRequest.objects.filter(
        status=CreateAccountRequest.STATUS_NEW)
    serializer_class = CreateAccountRequestSerializerForSubmit
    http_method_names = ('post', 'put', 'get')
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RequestFilter
    permission_classes = (CanSubmitCreateRequest,)


class CreateAccountRequestViewSetForReview(AbstractRequestViewSet, AllowDraftMixin, AllowRejectMixin):
    queryset = CreateAccountRequest.objects.filter(
        status=CreateAccountRequest.STATUS_PENDING_REVIEW_ITOO)
    serializer_class = CreateAccountRequestSerializerForReview
    http_method_names = ('put', 'get')
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RequestFilter
    permission_classes = (CanReviewCreateRequest,)


class CreateAccountRequestViewSetForExecute(AbstractRequestViewSet, AllowDraftMixin, AllowRejectMixin):
    queryset = CreateAccountRequest.objects.filter(
        status=CreateAccountRequest.STATUS_PENDING_REVIEW_ITOT)
    serializer_class = CreateAccountRequestSerializerForExecute
    http_method_names = ('put', 'get')
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RequestFilter
    permission_classes = (CanExecuteCreateRequest,)


class CreateAccountRequestViewSetForSetpUpComplete(AbstractRequestViewSet):
    queryset = CreateAccountRequest.objects.filter(
        status=CreateAccountRequest.STATUS_CONFIRMED_BY_HELPDESK)
    serializer_class = CreateAccountRequestSerializerForSetupComplete
    http_method_names = ('put', 'get')
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RequestFilter
    permission_classes = (CanCompleteSetupCreateAccount,)


class CreateAccountRequestViewSetForUserAck(AbstractRequestViewSet):
    queryset = CreateAccountRequest.objects.filter(
        status=CreateAccountRequest.STATUS_SETUP_COMPLETED)
    serializer_class = CreateAccountRequestSerializerForUserAck
    http_method_names = ('put', 'get')
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RequestFilter


class ResetPasswordRequestViewSet(AbstractRequestViewSet):
    # qs_class = ResetPasswordRequest.objects.select_related("related_user").all()
    queryset = ResetPasswordRequest.objects.select_related(
        "related_user").all()
    serializer_class = ResetPasswordRequestSerializer
    http_method_names = ('post', 'get')
    filter_backends = (filters.DjangoFilterBackend,
                       utils.SectionFilterBackend,)
    filterset_class = RequestFilter
    permission_classes = (CanResetPassword,)

    '''
    def create(self, request, *args, **kwargs):
        _data = {
            'csrfmiddlewaretoken': request.data['csrfmiddlewaretoken'],
            'new_password': request.data['new_password'],
            'related_user': request.data['related_user'],
        }
        serializer  = self.get_serializer(data =_data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
    '''


class AbstractAccountActionRequestViewSet(AbstractRequestViewSet):
    http_method_names = ('post', 'get')
    filter_backends = (filters.DjangoFilterBackend,
                       utils.SectionFilterBackend,)
    filterset_class = RequestFilter

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        data = []
        user_ids = request.data['user_ids']
        for _id in user_ids.split(','):
            serializer = self.get_serializer(data={'user_ids': _id})
            if serializer.is_valid():
                _ret_data = serializer.save()
                data.append(serializer.data)
        return Response(data)


class DisableAccountRequestViewSet(AbstractAccountActionRequestViewSet):
    queryset = DisableAccountRequest.objects.select_related(
        "related_user").all()
    serializer_class = DisableAccountRequestSerializer
    permission_classes = (CanDisableAccount,)


class EnableAccountRequestViewSet(AbstractAccountActionRequestViewSet):
    queryset = EnableAccountRequest.objects.select_related(
        "related_user").all()
    serializer_class = EnableAccountRequestSerializer
    permission_classes = (CanEnableAccount,)


class DeleteAccountRequestViewSet(AbstractAccountActionRequestViewSet):
    queryset = DeleteAccountRequest.objects.select_related(
        "related_user").all()
    serializer_class = DeleteAccountRequestSerializer
    permission_classes = (CanDeleteAccount,)


@api_view(['GET'])
def get_request_audit_log(request, request_id):
    return Response(utils.get_request_log(request_id))
    # return Response([])


class GenericRequest(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = BaseRequest.objects.select_related(
        'section').select_related('related_user').all()
    filter_backends = (utils.SectionFilterBackend,)
    permission_classes = (CanEnquireRequest,)
    serializer_class = BaseRequestSerializer


class GenericListRequests(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = BaseRequest.objects.select_related(
        'section').select_related('related_user').all().order_by('id')
    filter_backends = (OrderingFilter, utils.SectionFilterBackend,)
    ordering_fields = ['request_id', 'query_surname', 'query_given_name', 'query_post_title', 'section',
                       'creation_date', 'query_request_type_desc', 'query_status_desc', 'submission_date', 'last_modification_date', ]
    pagination_class = utils.JudPageNumberPagination
    permission_classes = (CanEnquireRequest,)
    serializer_class = BaseRequestListSerializer

    def _get_todo_criteria(self):
        ''' Default deny all criteria '''
        return_criteria = Q(pk__in=[])
        permissions = self.request.user.get_all_permissions()
        statuses_map = {
            'submit': CreateAccountRequest.STATUS_NEW,
            'review': CreateAccountRequest.STATUS_PENDING_REVIEW_ITOO,
            'execute': CreateAccountRequest.STATUS_PENDING_REVIEW_ITOT
        }
        create_list = [statuses_map.get(re.sub('_create_request$', '', re.sub('^uam_requests\.can_', '', permission)), -1)
                       for permission in permissions if re.search('^uam_requests\.can_.*_create_request$', permission)
                       ]
        if create_list:
            return_criteria = return_criteria | Q(
                instance_of=CreateAccountRequest, status__in=create_list)
        update_list = [statuses_map.get(re.sub('_update_request$', '', re.sub('^uam_requests\.can_', '', permission)), -1)
                       for permission in permissions if re.search('^uam_requests\.can_.*_update_request$', permission)
                       ]
        if update_list:
            return_criteria = return_criteria | Q(
                instance_of=UpdateAccountRequest, status__in=update_list)
        return return_criteria

    # def get_serializer_class(self):
    #     '''
    #     In order to minimize call to DB, only get the detail serializer when retrieving one specific record, otherwise, return the list serializer.
    #     '''
    #     if self.action == 'retrieve':
    #         return BaseRequestSerializer
    #     else:
    #         return BasicBaseRequestSerializer

    def get_queryset(self):
        param = self.request.query_params
        request_id = param.get('request_id', None)
        # request_by = param.get('request_by', None)
        request_status = param.get('request_status', None)
        request_type = param.get('request_type', None)
        query_surname = param.get('surname', None)
        query_given_name = param.get('given_name', None)
        section = param.get('section', None)
        only_todo = param.get('only_todo', None)
        account_type = param.get('account_type', None)
        uam_id = param.get('uam_id', None)
        qs = super().get_queryset()

        if uam_id:
            qs = qs.filter(related_user__uam_id=uam_id)
        if request_type:
            if (request_type == 'CreateAccount'):
                qs = qs.instance_of(CreateAccountRequest)
            elif (request_type == 'UpdateAccount'):
                qs = qs.instance_of(UpdateAccountRequest)
            elif (request_type == 'DeleteAccount'):
                qs = qs.instance_of(DeleteAccountRequest)
            elif (request_type == 'ResetPassword'):
                qs = qs.instance_of(ResetPasswordRequest)
            elif (request_type == 'DisableAccount'):
                qs = qs.instance_of(DisableAccountRequest)
            elif (request_type == 'ReenableAccount'):
                qs = qs.instance_of(EnableAccountRequest)
        if only_todo:
            qs = qs.filter(self._get_todo_criteria())
        if request_id:
            qs = qs.filter(request_id__contains=request_id)
        if request_status:
            qs = qs.filter(status=request_status)
        if query_surname:
            name_list = query_surname.split()
            for name in name_list:
                qs = qs.filter(query_surname__contains=name)
        if query_given_name:
            name_list = query_given_name.split()
            for name in name_list:
                qs = qs.filter(query_given_name__contains=name)
        if section:
            qs = qs.filter(section=section)
        if account_type:
            qs = qs.annotate(
                account_type_out=Case(
                    # When(instance_of=CreateAccountRequest, then=F('accountrequest__account_type')),
                    # When(instance_of=UpdateAccountRequest, then=F('accountrequest__account_type')),
                    When(instance_of=AccountRequest, then=F(
                        'accountrequest__account_type')),
                    default=F('related_user__account_type'),
                    output_field=models.IntegerField()
                )
            )
            # qs = qs.filter(related_user__account_type=account_type)
            qs = qs.filter(account_type_out=account_type)
        qs = qs.values(
            'id', 'request_id', 'query_surname', 'query_given_name', 'section__id', 'section__code', 'query_post_title', 'submission_date',
            'query_request_type_desc', 'query_status_desc', 'creation_date', 'last_modification_date',
        )
        return qs


class RequestFileView(APIView):
    parser_classes = (MultiPartParser, FormParser,)

    def post(self, request, request_id, *args, **kwargs):
        rtn_arr = []
        if request_id:
            try:
                req = BaseRequest.objects.get(id=request_id)
            except BaseRequest.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            tmp_status = request.data.get('status', req.status)
            for file in request.data.getlist('uploadfile'):
                save_file = RequestFile.objects.create(
                    file=file, file_name=file.name, request=req, status=tmp_status)
                rtn_arr.append(save_file.id)
            return Response(rtn_arr, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


# def index(request):
#     return render(request, 'index.html', context={})
