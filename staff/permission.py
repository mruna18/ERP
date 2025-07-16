# staff/permissions.py

from rest_framework.permissions import BasePermission
from companies.models import Company
from staff.models import *
from .utils import *

class StaffPermission(BasePermission):
    def has_permission(self, request, view):
        action = view.action if hasattr(view, "action") else request.method.lower()
        if action == "post":
            action = "create"
        elif action == "get":
            action = "view"
        elif action in ["put", "patch"]:
            action = "edit"
        elif action == "delete":
            action = "delete"

        # Determine company_id from request
        company_id = (
            request.data.get("company_id") or
            request.data.get("company") or
            request.query_params.get("company") or
            view.kwargs.get("company_id")
        )

        if not company_id:
            raise CustomApiException(400, "company_id is required")

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            raise CustomApiException(404, "Company not found.")

        try:
            staff = StaffProfile.objects.get(user=request.user, company=company, is_active=True)
        except StaffProfile.DoesNotExist:
            raise CustomApiException(403, "You are not associated with selected company.")

        page_code = getattr(view, "page", None)
        if not page_code:
            raise CustomApiException(403, "This view is not properly configured with `page`.")

        allowed_codes = [perm.code for perm in staff.role.permissions.all()]

        if page_code not in allowed_codes:
            raise CustomApiException(403, f"Access denied for '{page_code}'.")

        return True


#! has permission
class HasCustomPermission(BasePermission):
    def has_permission(self, request, view):
        required_permission = getattr(view, 'required_permission', None)
        company_id = (
            request.data.get("company_id") or
            request.query_params.get("company_id") or
            view.kwargs.get("company_id")
        )

        if not required_permission or not company_id:
            return False

        try:
            staff = StaffProfile.objects.get(
                username=request.user.username,
                company_id=company_id,
                is_active=True
            )
            return staff.role.permissions.filter(code=required_permission).exists()
        except StaffProfile.DoesNotExist:
            return False

