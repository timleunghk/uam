from .models import (
    Section, AdGroup, LnGroup, MasterRank, ActiveDirectoryOU, LnAccountType, LnClientLicense,
    LnMPSRange, LnMailFileOwner, LnMailServer, LnMailSystem, LnMailTemplate, LnLicenseType,
    LnAddressDomain,
)
from django.db.models import Q
from rest_framework import viewsets
from .models import (
    Section, AdGroup, LnGroup, MasterRank, ActiveDirectoryOU, LnAccountType, LnClientLicense,
    LnMPSRange, LnMailFileOwner, LnMailServer, LnMailSystem, LnMailTemplate, LnLicenseType,
    LnAddressDomain, DpEmployeeType, DpRankCode, DpStaffGroup,
)
from .serializers import (
    SectionSerializer, AdGroupSerializer, LnGroupSerializer, MasterRankSerializer, ADOUSerializer,
    LnAccountTypeSerializer, LnClientLicenseSerializer,
    LnMPSRangeSerializer, LnMailFileOwnerSerializer, LnMailServerSerializer, LnMailSystemSerializer,
    LnMailTemplateSerializer, LnLicenseTypeSerializer, LnAddressDomainSerializer,
    DpEmployeeTypeSerializer, DpRankCodeSerializer, DpStaffGroupSerializer,
)


# class TitleView(AbstractRequestViewSet, AllowDraftOnCreateMixin):
#     queryset = Title.objects.all()
#     serializer_class = TitleSerializer
#     http_method_names = ('post', 'put', 'get')

# class MasterRankView(AbstractRequestViewSet, AllowDraftOnCreateMixin):
#     queryset = MasterRank.objects.all()
#     serializer_class=MasterRankSerializer
#     http_method_names = ('post', 'put', 'get')

# class AccountTypeView(AbstractRequestViewSet, AllowDraftOnCreateMixin):
#     queryset = AccountType.objects.all()
#     serializer_class=AccountTypeSerializer
#     http_method_names = ('post', 'put', 'get')

class SectionListView(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'code'
    queryset = Section.objects.all()
    serializer_class = SectionSerializer

    def list(self, request, *args, **kwargs):
        search_str = request.query_params.get('section', None)
        if search_str is not None:
            for instr in search_str.split():
                self.queryset = self.queryset.filter(
                    Q(code__icontains=instr) | Q(description__icontains=instr))
        else:
            self.queryset = self.queryset.none()
        return super().list(request, *args, **kwargs)


class AdGroupListView(viewsets.ReadOnlyModelViewSet):
    queryset = AdGroup.objects.filter(active=True).order_by('name')
    serializer_class = AdGroupSerializer


class LnGroupListView(viewsets.ReadOnlyModelViewSet):
    queryset = LnGroup.objects.filter(active=True).order_by('name')
    serializer_class = LnGroupSerializer


class MasterRankListView(viewsets.ReadOnlyModelViewSet):
    # lookup_field = 'value'
    queryset = MasterRank.objects.all()
    serializer_class = MasterRankSerializer

    def list(self, request, *args, **kwargs):
        search_str = request.query_params.get('rank', None)
        if search_str is not None:
            for instr in search_str.split():
                self.queryset = self.queryset.filter(
                    Q(value__icontains=instr) | Q(description__icontains=instr))
        else:
            self.queryset = self.queryset.none()
        return super().list(request, *args, **kwargs)


class ActiveDirectoryOUListView(viewsets.ReadOnlyModelViewSet):
    queryset = ActiveDirectoryOU.objects.filter(active=True).order_by('name')
    serializer_class = ADOUSerializer


class LnAccountTypeListView(viewsets.ReadOnlyModelViewSet):
    queryset = LnAccountType.objects.filter(active=True).order_by('name')
    serializer_class = LnAccountTypeSerializer


class LnClientLicenseListView(viewsets.ReadOnlyModelViewSet):
    queryset = LnClientLicense.objects.filter(active=True).order_by('name')
    serializer_class = LnClientLicenseSerializer


class LnMPSRangeListView(viewsets.ReadOnlyModelViewSet):
    queryset = LnMPSRange.objects.filter(active=True).order_by('name')
    serializer_class = LnMPSRangeSerializer


class LnMailFileOwnerListView(viewsets.ReadOnlyModelViewSet):
    queryset = LnMailFileOwner.objects.filter(active=True).order_by('name')
    serializer_class = LnMailFileOwnerSerializer


class LnMailServerListView(viewsets.ReadOnlyModelViewSet):
    queryset = LnMailServer.objects.filter(active=True).order_by('name')
    serializer_class = LnMailServerSerializer


class LnMailSystemListView(viewsets.ReadOnlyModelViewSet):
    queryset = LnMailSystem.objects.filter(active=True).order_by('name')
    serializer_class = LnMailSystemSerializer


class LnMailTemplateListView(viewsets.ReadOnlyModelViewSet):
    queryset = LnMailTemplate.objects.filter(active=True).order_by('name')
    serializer_class = LnMailTemplateSerializer


class LnLicenseTypeListView(viewsets.ReadOnlyModelViewSet):
    queryset = LnLicenseType.objects.filter(active=True).order_by('name')
    serializer_class = LnLicenseTypeSerializer


class LnAddressDomainListView(viewsets.ReadOnlyModelViewSet):
    queryset = LnAddressDomain.objects.filter(active=True).order_by('name')
    serializer_class = LnAddressDomainSerializer


class DpRankCodeListView(viewsets.ReadOnlyModelViewSet):
    queryset = DpRankCode.objects.filter(active=True).order_by('name')
    serializer_class = DpRankCodeSerializer


class DpEmployeeTypeListView(viewsets.ReadOnlyModelViewSet):
    queryset = DpEmployeeType.objects.filter(active=True).order_by('name')
    serializer_class = DpEmployeeTypeSerializer


class DpStaffGroupListView(viewsets.ReadOnlyModelViewSet):
    queryset = DpStaffGroup.objects.filter(active=True).order_by('name')
    serializer_class = DpStaffGroupSerializer
