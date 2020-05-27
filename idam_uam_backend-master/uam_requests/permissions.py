from rest_framework import permissions


class CanSubmitCreateRequest(permissions.BasePermission):

    def has_permission(self, request, view):
        return 'uam_requests.can_submit_create_request' in request.user.get_all_permissions()


class CanReviewCreateRequest(permissions.BasePermission):

    def has_permission(self, request, view):
        return 'uam_requests.can_review_create_request' in request.user.get_all_permissions()


class CanExecuteCreateRequest(permissions.BasePermission):

    def has_permission(self, request, view):
        return 'uam_requests.can_execute_create_request' in request.user.get_all_permissions()


class CanSubmitUpdateRequest(permissions.BasePermission):

    def has_permission(self, request, view):
        return 'uam_requests.can_submit_update_request' in request.user.get_all_permissions()


class CanReviewUpdateRequest(permissions.BasePermission):

    def has_permission(self, request, view):
        return 'uam_requests.can_review_update_request' in request.user.get_all_permissions()


class CanExecuteUpdateRequest(permissions.BasePermission):

    def has_permission(self, request, view):
        return 'uam_requests.can_execute_update_request' in request.user.get_all_permissions()


class CanEnquireRequest(permissions.BasePermission):
    def has_permission(self, request, view):
        return 'uam_requests.can_enquire_request' in request.user.get_all_permissions()


class CanEnquireAccount(permissions.BasePermission):
    def has_permission(self, request, view):
        return 'uam_requests.can_enquire_account' in request.user.get_all_permissions()


class CanDisableAccount(permissions.BasePermission):
    def has_permission(self, request, view):
        return 'uam_requests.can_disable_account' in request.user.get_all_permissions()


class CanEnableAccount(permissions.BasePermission):
    def has_permission(self, request, view):
        return 'uam_requests.can_enable_account' in request.user.get_all_permissions()


class CanDeleteAccount(permissions.BasePermission):
    def has_permission(self, request, view):
        return 'uam_requests.can_delete_account' in request.user.get_all_permissions()


class CanResetPassword(permissions.BasePermission):
    def has_permission(self, request, view):
        return 'uam_requests.can_reset_password' in request.user.get_all_permissions()


class CanCompleteSetupCreateAccount(permissions.BasePermission):
    def has_permission(self, request, view):
        return 'uam_requests.can_complete_create_request' in request.user.get_all_permissions()


def can_maintain_all_section(request):
    if hasattr(request, 'user'):
        return 'uam_requests.can_manage_all_sections' in request.user.get_all_permissions()
    return False
