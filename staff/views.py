from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from rest_framework import status
from staff.models import *
from companies.models import Company  
from django.db import transaction
from .serializer import *
from .permission import *
from django.contrib.auth.models import User
from rest_framework.viewsets import ModelViewSet

#! STAFF
class CreateStaffView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Staff"
    required_permission = "create"

    def post(self, request):
        data = request.data
        username = data.get('username')
        email = data.get('email', '')
        password = data.get('password')
        role_id = data.get('role_id')
        company_id = data.get('company_id')

        if not all([username, password, role_id, company_id]):
            return Response({"msg": "Missing required fields", "status": 500})

        try:
            company = Company.objects.get(id=company_id)
            role = Role.objects.get(id=role_id, company=company, deleted=False)
        except Company.DoesNotExist:
            return Response({"msg": "Company not found", "status": 500})
        except Role.DoesNotExist:
            return Response({"msg": "Role not found in this company", "status": 500})

        # Get or create user
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.email = email
            user.set_password(password)
            user.save()
        else:
           
            pass

        # Check if this username is already assigned in this company
        if StaffProfile.objects.filter(user=user, company=company).exists():
            return Response({"msg": "Username already exists in this company", "status": 500})

        # Create staff profile
        staff = StaffProfile.objects.create(
            user=user,
            company=company,
            job_role=role,
            username=username,
            email=email,
            password=make_password(password),  
            is_active=True
        )

        serializer = StaffProfileSerializer(staff)
        return Response({
            "msg": "Staff created successfully",
            "data": serializer.data,
            "status": 201
        }, status=status.HTTP_201_CREATED)


class UpdateStaffView(APIView):
    permission_classes = [IsAuthenticated, HasModulePermission, IsCompanyAdminOrAssigned]
    required_module = "Staff"
    required_permission = "update"  

    def post(self, request):
        data = request.data
        staff_id = data.get('staff_id')
        name = data.get('name')
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        role_id = data.get('role_id')
        company_id = data.get('company_id') or data.get('company') or request.headers.get("company")

        if not company_id:
            return Response({"detail": "Company ID is required."})

        if not staff_id:
            return Response({"detail": "Staff ID required."})

        try:
            staff = StaffProfile.objects.get(id=staff_id, company_id=company_id, is_active=True)
        except StaffProfile.DoesNotExist:
            return Response({"detail": "Staff not found."}, status=status.HTTP_404_NOT_FOUND)

        # Update StaffProfile fields
        if name:
            staff.name = name
        if email:
            staff.email = email
        if username:
            staff.username = username
        if password:
            staff.password = make_password(password)
        if role_id:
            try:
                role = Role.objects.get(id=role_id, company_id=company_id, deleted=False)
                staff.job_role = role
            except Role.DoesNotExist:
                return Response({"detail": "Role not found in this company."}, status=404)

        staff.save()

        # Also update the related user object
        user = staff.user
        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.set_password(password)
        user.save()

        return Response({"detail": "Staff updated successfully."})

    
#! ROLE
class CreateStaffRoleView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Roles"
    required_permission = "create"

    def post(self, request):
        data = request.data
        name = data.get('name')
        description = data.get('description', '')
        company_id = data.get('company')
        module_permissions_data = data.get('module_permissions', [])

        if not name or not company_id:
            return Response({"msg": "Missing required fields! name and compnay_id is required", "status": 500})

        if Role.objects.filter(name=name, company_id=company_id, deleted=False).exists():
            return Response({"msg": "Role already exists", "status": 500})

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({"msg": "Company not found", "status": 500})

        # Create role
        role = Role.objects.create(name=name, description=description, company=company)

        for perm in module_permissions_data:
            required_module_name = perm.get("required_module")
            if not required_module_name:
                return Response({"msg": "Module name is required in permissions", "status": 500})

            try:
                module = Module.objects.get(name=required_module_name)
            except Module.DoesNotExist:
                return Response({"msg": f"Module '{required_module_name}' does not exist", "status": 500})

            ModulePermission.objects.create(
                job_role=role,
                company=company,
                # module=module,
                required_module=module.name,
                can_view=perm.get("can_view", False),
                can_create=perm.get("can_create", False),
                can_edit=perm.get("can_edit", False),
                can_delete=perm.get("can_delete", False),
                can_view_specific=perm.get("can_view_specific", False),
                can_get_using_post=perm.get("can_get_using_post", False),
            )

        return Response({
            "msg": "Role with permissions created successfully",
            "data": {
                "id": role.id,
                "name": role.name,
                "company": company.name,
            },
            "status": 201
        })

    
class ListStaffRolesView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Roles"
    required_permission = "view"
    

    def get(self, request, company_id):
        user = request.user
        # Ensure user is allowed to access roles for this company
        if hasattr(user, 'company') and user.company.id != int(company_id):
            return Response({
                "msg": "You are not authorized to view roles for this company.",
                "status": 500
            })

        roles = Role.objects.filter(company_id=company_id, deleted=False)
        serializer = StaffRoleSerializer(roles, many=True)
        return Response({
            "msg": "Roles fetched successfully",
            "data": serializer.data,
            "status": 200
        })
    
class UpdateStaffRoleView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Roles"
    required_permission = "update"

    def put(self, request, role_id):
        data = request.data
        name = data.get("name")
        description = data.get("description", "")
        company_id = data.get("company_id")
        module_permissions = data.get("module_permissions", [])

        if not name or not company_id:
            return Response({"msg": "Missing required fields", "status": 500})

        try:
            role = Role.objects.get(id=role_id, company_id=company_id, deleted=False)
        except Role.DoesNotExist:
            return Response({"msg": "Role not found", "status": 500})

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({"msg": "Company not found", "status": 500})

        with transaction.atomic():
            role.name = name
            role.description = description
            role.save()

            # Delete old module permissions for this role
            ModulePermission.objects.filter(job_role=role).delete()

            for mod_perm in module_permissions:
                required_module = mod_perm.get("required_module")
                try:
                    module = Module.objects.get(name=required_module)
                except Module.DoesNotExist:
                    return Response({"msg": f"Module '{required_module}' not found", "status": 500})

                ModulePermission.objects.create(
                    job_role=role,
                    company=company,
                    required_module=module.name,
                    can_view=mod_perm.get("can_view", False),
                    can_create=mod_perm.get("can_create", False),
                    can_edit=mod_perm.get("can_edit", False),
                    can_delete=mod_perm.get("can_delete", False),
                    can_view_specific=mod_perm.get("can_view_specific", False),
                    can_get_using_post=mod_perm.get("can_get_using_post", False),
                )

        return Response({
            "msg": "Role updated successfully",
            "role_id": role.id,
            "status": 200
        })

class SoftDeleteStaffRoleView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Roles"
    required_permission = "delete"
   

    def delete(self, request, pk):
        try:
            role = Role.objects.get(pk=pk, deleted=False)
        except Role.DoesNotExist:
            return Response({"msg": "Role not found", "status": 500})

        #  Only allow deletion if the role belongs to the user's company
        if hasattr(request.user, 'company_id') and role.company_id != request.user.company_id:
            return Response({"msg": "Unauthorized to delete this role", "status": 500})

        role.deleted = True
        role.save()

        return Response({
            "msg": f"Role '{role.name}' soft deleted successfully",
            "status": 200
        })


#!Permission
# class UpdateRolePermissionsView(APIView):
#     permission_classes =[IsAuthenticated, IsCompanyAdminOrAssigned]
#    

#     def post(self, request):
#         role_id = request.data.get('role_id')
#         permission_ids = request.data.get('permission_ids', [])

#         if not role_id or not isinstance(permission_ids, list):
#             raise CustomApiException(400, "role_id and permission_ids are required.")

#         try:
#             role = Role.objects.get(id=role_id, deleted=False)
#         except Role.DoesNotExist:
#             raise CustomApiException(404, "Role not found.")

#         permissions = CustomPermission.objects.filter(id__in=permission_ids)

#         if permissions.count() != len(permission_ids):
#             raise CustomApiException(400, "One or more permission IDs are invalid.")

#         role.permissions.set(permissions)

#         return Response({
#             "status": 200,
#             "message": "Permissions updated successfully.",
#             "role": role.name,
#             "permissions": [p.code for p in permissions]
#         })

    
class ListAllPermissionsView(APIView):
    permission_classes = [IsAuthenticated]
    

    def get(self, request):
        # company_id = request.headers.get('company')  
        company_id = get_company_id(request)

        # print(company_id)
        user = request.user

        try:
            staff = StaffProfile.objects.get(user=user, company=company_id, is_active=True)
        except StaffProfile.DoesNotExist:
            return Response({"detail": "Not a staff member or inactive.","status":500})

        if not staff.job_role:
            return Response({"detail": "No role assigned.","status":500})

        permissions = ModulePermission.objects.filter(job_role=staff.job_role, company_id=company_id)
        data = [
            {
                "module": perm.required_module,
                "can_view": perm.can_view,
                "can_create": perm.can_create,
                "can_edit": perm.can_edit,
                "can_delete": perm.can_delete
            }
            for perm in permissions
        ]

        return Response({
            "user_id": user.id,
            "company_id": company_id,
            "role": staff.job_role.name,
            "permissions": data
        })

#!.
class MyCompaniesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        companies_data = []
        admin_companies = []
        staff_companies = []
        selected_company_id = None

        # Check if user is a Customer (admin user)
        try:
            customer = Customer.objects.get(user=user)
            companies = Company.objects.filter(owner=customer, is_active=True)
            for c in companies:
                comp_data = {
                    "id": c.id,
                    "name": c.name,
                    "gst_number": c.gst_number,
                    "phone": c.phone,
                    "created_at": c.created_at,
                }
                companies_data.append(comp_data)
                admin_companies.append(comp_data)
            selected_company_id = customer.selected_company.id if customer.selected_company else None

        except Customer.DoesNotExist:
            # If not customer, check if user is staff
            staff_profiles = StaffProfile.objects.filter(user=user, is_active=True)
            for sp in staff_profiles:
                c = sp.company
                comp_data = {
                    "id": c.id,
                    "name": c.name,
                    "gst_number": c.gst_number,
                    "phone": c.phone,
                    "created_at": c.created_at,
                    "role": sp.job_role.name,
                }
                companies_data.append(comp_data)
                staff_companies.append(comp_data)

        return Response({
            "data": companies_data,
            "admin": admin_companies,
            "staff": staff_companies,
            "selected_company_id": selected_company_id,
        })

# from django.core.cache import cache  # ✅ Import cache

# class MyCompaniesView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         cache_key = f"my_companies_{user.id}"  # ✅ Unique cache key per user
#         print(f"🗝️ Cache key: {cache_key}")

#         cached_data = cache.get(cache_key)
#         if cached_data:
#             print("✅ Returning data from cache")
#             return Response(cached_data)

#         print("🔄 Cache miss — fetching from DB...")
#         companies = Company.objects.filter(
#             staffprofile__user=user, is_active=True
#         ).distinct()

#         data = [
#             {
#                 "id": company.id,
#                 "name": company.name,
#             } for company in companies
#         ]

#         response_data = {
#             "status": 200,
#             "companies": data
#         }

#         # ✅ Store in cache for 5 minutes
#         cache.set(cache_key, response_data, timeout=60 * 5)
#         print("💾 Data cached for 5 minutes")

#         return Response(response_data)



# class AssignRoleToStaffView(APIView):
#     permission_classes =[IsAuthenticated, IsCompanyAdminOrAssigned]
#    

#     def put(self, request, company_id, pk):
#         role_id = request.data.get('role_id')
#         if not role_id:
#             return Response({"msg": "role_id is required", "status": 500})

#         try:
#             staff = StaffProfile.objects.get(pk=pk, company_id=company_id, is_active=True)
#         except StaffProfile.DoesNotExist:
#             return Response({"msg": "Staff not found in this company", "status": 500})

#         try:
#             role = Role.objects.get(id=role_id, company_id=company_id, deleted=False)
#         except Role.DoesNotExist:
#             return Response({"msg": "Role not found in this company", "status": 500})

#         staff.role = role
#         staff.save()

#         return Response({
#             "msg": "Role assigned successfully",
#             "data": {
#                 "staff_id": staff.id,
#                 "username": staff.username,
#                 "company": staff.company.name,
#                 "new_role": role.name
#             },
#             "status": 200
#         })


#! modulepermission

class ModulePermissionViewSet(ModelViewSet):
    queryset = ModulePermission.objects.all()
    serializer_class = ModulePermissionSerializer
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Permission"
    required_permission = "view"

    def get_queryset(self):
        company_id = self.request.query_params.get('company_id')
        if company_id:
            return self.queryset.filter(company_id=company_id)
        return self.queryset.none()
    
#! module
class CreateModuleView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Modules"
    required_permission = "create"

    def post(self, request):
        serializer = ModuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

class ListModulesView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Modules"
    required_permission = "view"
    def get(self, request):
        modules = Module.objects.all()
        serializer = ModuleSerializer(modules, many=True)
        return Response(serializer.data)

class RetrieveModuleView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Modules"
    required_permission = "view"
    def get(self, request, pk):
        try:
            module = Module.objects.get(pk=pk)
        except Module.DoesNotExist:
            return Response({"msg": "Module not found"})
        serializer = ModuleSerializer(module)
        return Response(serializer.data)

class UpdateModuleView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Modules"
    required_permission = "update"
    def put(self, request, pk):
        try:
            module = Module.objects.get(pk=pk)
        except Module.DoesNotExist:
            return Response({"msg": "Module not found"})
        serializer = ModuleSerializer(module, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

class DeleteModuleView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Modules"
    required_permission = "delete"
    def delete(self, request, pk):
        try:
            module = Module.objects.get(pk=pk)
        except Module.DoesNotExist:
            return Response({"msg": "Module not found"})
        module.delete()
        return Response({"msg": "Module deleted"})