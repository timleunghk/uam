from django.contrib import admin
from .models import (Section, AdGroup, LnGroup, MasterRank, ActiveDirectoryOU, LnAccountType,
                     LnAddressDomain, LnClientLicense, LnLicenseType, LnMailFileOwner, LnMailServer, LnMailSystem,
                     LnMailTemplate, LnMPSRange, DpEmployeeType, DpRankCode, DpStaffGroup)


class SectionAdmin(admin.ModelAdmin):
    search_fields = ('description', 'code',)


class SimpleGroupAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class MasterRankAdmin(admin.ModelAdmin):
    search_fields = ('value', 'description', )


# Register your models here.
admin.site.register(AdGroup, SimpleGroupAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(LnGroup, SimpleGroupAdmin)
admin.site.register(MasterRank, MasterRankAdmin)
admin.site.register(ActiveDirectoryOU, SimpleGroupAdmin)
admin.site.register(LnAccountType, SimpleGroupAdmin)
admin.site.register(LnAddressDomain, SimpleGroupAdmin)
admin.site.register(LnClientLicense, SimpleGroupAdmin)
admin.site.register(LnLicenseType, SimpleGroupAdmin)
admin.site.register(LnMailFileOwner, SimpleGroupAdmin)
admin.site.register(LnMailServer, SimpleGroupAdmin)
admin.site.register(LnMailSystem, SimpleGroupAdmin)
admin.site.register(LnMailTemplate, SimpleGroupAdmin)
admin.site.register(LnMPSRange, SimpleGroupAdmin)
admin.site.register(DpEmployeeType, SimpleGroupAdmin)
admin.site.register(DpRankCode, SimpleGroupAdmin)
admin.site.register(DpStaffGroup, SimpleGroupAdmin)
