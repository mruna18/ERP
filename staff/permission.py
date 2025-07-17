from rest_framework.permissions import BasePermission
from companies.models import Company
from staff.models import StaffProfile
from customer.models import Customer
from .models import ModulePermission  # adjust import based on where you keep it


def get_company_id(request, view):
    return (
        request.data.get("company_id")
        or request.data.get("company")
        or request.query_params.get("company")
        or request.query_params.get("company_id")
        or view.kwargs.get("company_id")
    )


class IsCompanyAdminOrAssigned(BasePermission):
    """
    Allows access to:
    - Company owner (Customer)
    - Assigned Staff
    """

    def has_permission(self, request, view):
        company_id = get_company_id(request, view)
        if not company_id:
            return False

        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            return False

        # Allow if customer is owner of the company
        if Company.objects.filter(id=company_id, owner=customer, is_active=True).exists():
            return True

        # Allow if staff assigned to company
        return StaffProfile.objects.filter(user=request.user, company_id=company_id, is_active=True).exists()


class HasModulePermission(BasePermission):
    """
    Checks if a staff has required module permission based on HTTP method
    """

    def has_permission(self, request, view):
        user = request.user
        company_id = get_company_id(request, view)
        module_name = getattr(view, 'module_name', None)

        if not user or not user.is_authenticated or not company_id or not module_name:
            return False

        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            customer = None

        # Owner has full access
        if customer and Company.objects.filter(id=company_id, owner=customer, is_active=True).exists():
            return True

        # Now check staff permissions
        staff = StaffProfile.objects.filter(user=request.user, company_id=company_id, is_active=True).first()
        if not staff or not staff.role:
            return False

        method_map = {
            'GET': 'can_view',
            'POST': 'can_create',
            'PUT': 'can_edit',
            'PATCH': 'can_edit',
            'DELETE': 'can_delete'
        }

        action_field = method_map.get(request.method)
        if not action_field:
            return False

        return ModulePermission.objects.filter(
            job_role=staff.role,
            company_id=company_id,
            module_name=module_name,
            **{action_field: True}
        ).exists()
