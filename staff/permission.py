from rest_framework.permissions import BasePermission
from companies.models import Company
from staff.models import StaffProfile
from customer.models import Customer
from .models import ModulePermission
from rest_framework.response import Response
from parties.models import *


# def get_company_id(request, view=None):
#     return (
#         request.headers.get("company") or
#         request.data.get("company_id") or
#         request.data.get("company") or
#         request.query_params.get("company_id") or
#         request.query_params.get("company") or
#         (view.kwargs.get("company_id") if view else None)
#     )

def get_company_id(request, view=None):
    return (
        request.headers.get("company") or
        request.data.get("company_id") or
        request.data.get("company") or
        request.query_params.get("company_id") or
        request.query_params.get("company") or
        (view.kwargs.get("company_id") if view else None) or
        get_company_from_instance(view, request)
    )

def get_company_from_instance(view, request):
    try:
        if hasattr(view, 'kwargs') and 'pk' in view.kwargs:
            party = Party.objects.get(pk=view.kwargs['pk'], deleted=False)
            return party.company_id
    except Party.DoesNotExist:
        return None


class IsCompanyAdminOrAssigned(BasePermission):
    def has_permission(self, request, view):
        company_id = get_company_id(request, view)
        #print(f" [IsCompanyAdminOrAssigned] Company ID: {company_id}")

        if not company_id:
            # #print("No company ID found.")
            return False

        try:
            customer = Customer.objects.get(user=request.user)
            #print(f" Customer found: {customer}")
        except Customer.DoesNotExist:
            customer = None
            #print(" Customer does not exist.")

        if customer and Company.objects.filter(id=company_id, owner=customer, is_active=True).exists():
            #print(" User is the company owner")
            return True

        is_staff = StaffProfile.objects.filter(user=request.user, company_id=company_id, is_active=True).exists()
        #print(f"Staff assigned to company: {is_staff}")

        return is_staff


class HasModulePermission(BasePermission):
    def has_permission(self, request, view):
        required_module = getattr(view, 'required_module', None)
        required_permission = getattr(view, 'required_permission', None)

        if not required_module or not required_permission:
            return False

        company_id = get_company_id(request, view)
        if not company_id:
            return False

        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            customer = None

        if customer and Company.objects.filter(id=company_id, owner=customer, is_active=True).exists():
            return True

        staff = StaffProfile.objects.filter(user=request.user, company_id=company_id, is_active=True).first()
        if not staff or not staff.job_role:
            #print("❌ No staff or no job role.")
            return False
        
        #print("🔐 Module:", required_module)
        #print("🔐 Permission:", required_permission)
        #print("🔐 Company:", company_id)
        #print("🔐 Role ID:",  staff.job_role.id if staff.job_role else None)

        permission_qs = ModulePermission.objects.filter(
            job_role=staff.job_role,
            required_module__iexact=required_module,
            company_id=company_id
        ).first()

        if not permission_qs:
            #print("❌ No permission found for this module and role.")
            return False
    

        #print("🔐 Module:", required_module)
        #print("🔐 Permission:", required_permission)
        #print("🔐 Company:", company_id)
        #print("🔐 Role ID:",  staff.job_role.id if staff.job_role else None)
        #print("🔐 Permission Check Result:", getattr(permission_qs, f"can_{required_permission}", False))

        return getattr(permission_qs, f"can_{required_permission}", False)


#! check the staff and customer

# def get_user_context(request, company_id):
#     """
#     Returns a dict: {'customer': <Customer obj> or None, 'staff': <StaffProfile obj> or None}
#     Raises error if user is not authorized for this company.
#     """
#     customer = Customer.objects.filter(user=request.user).first()
#     staff = None

#     if not customer:
#         staff = StaffProfile.objects.filter(user=request.user, company_id=company_id, is_active=True).first()
#         if not staff:
#             return None  # Unauthorized

#     return {
#         'customer': customer,
#         'staff': staff
#     }

def get_user_context(request, company_id):
    """
    Returns a tuple: (customer, company, error Response or None)
    """
    customer = Customer.objects.filter(user=request.user).first()
    staff = None
    company = None

    if customer:
        company = Company.objects.filter(id=company_id, customer=customer).first()
        if not company:
            return customer, None, Response({"detail": "Invalid company for this customer."}, status=403)
    else:
        staff = StaffProfile.objects.filter(user=request.user, company_id=company_id, is_active=True).first()
        if not staff:
            return None, None, Response({"detail": "Unauthorized staff."}, status=403)
        company = staff.company

    return customer or staff, company, None



#! 
def extract_company_from_context(context):
    if context['customer']:
        return context['customer'].company
    elif context['staff']:
        return context['staff'].company
    return 

#! customer module
class IsSuperAdminOrSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or obj.user == request.user