from rest_framework import serializers
from interface.models import ExternalSync

class ExternalSyncSerializer(serializers.ModelSerializer):
    sync_type_desc = serializers.SerializerMethodField()
    class Meta:
        model = ExternalSync
        fields = '__all__'

    def get_sync_type_desc(self, instance):
        return ExternalSync.SYNC_TYPES_DICT.get(instance.sync_type)