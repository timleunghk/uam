# from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from common import utils
from interface.models import ExternalSync
from interface.serializers import ExternalSyncSerializer


class RomaViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        with utils.get_common_nameko_client() as client:
            roma_full_name, hkid = client.idam_roma_service.get_roma_info(pk)
            if hkid:
                hkid = hkid[:4]
            # print(roma_full_name, hkid)
            return Response({'id': pk, 'roma_id': pk, 'roma_full_name': roma_full_name, 'hkid': hkid})
        # return Response({'id': pk, 'roma_id': '12%s' % pk, 'roma_full_name': 'ROMA Full Name %s' % pk, 'hkid': 'A1%s' % pk})


class ExternalSyncViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = ExternalSync.objects.all()
    serializer_class = ExternalSyncSerializer

    def get_queryset(self):
        param = self.request.query_params
        # qs = self.queryset
        request_id = param.get('request_id', None)
        qs = self.queryset.filter(request_id=request_id)
        return qs
