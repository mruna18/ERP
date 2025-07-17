from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from staff.models import *
from companies.models import Company  
from django.db import transaction
from .serializer import *
from .permission import *
from django.contrib.auth.models import User
from rest_framework.viewsets import ModelViewSet

class CreateStaffView(APIView):
    # permission_classes =[IsAuthenticated, IsCompanyAdminOrAssigned]
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
            return Response({"msg": "Missing required fields", "status": 400})

        # Check if username already exists in the User table for this company
        if User.objects.filter(username=username).exists():
            return Response({"msg": "Username already exists", "status": 400})

        # Create the User first
        user = User.objects.create_user(username=username, email=email, password=password)

        # Create the StaffProfile
        role = Role.objects.get(id=role_id, company_id=company_id, deleted=False)
        company = Company.objects.get(id=company_id)
        staff = StaffProfile.objects.create(
            company=company,
            role=role,
            username=username,
            email=email,
            password=password,  # Optionally store it, but not recommended
            is_active=True
        )

        return Response({
            "msg": "Staff created successfully",
            "data": {
                "id": staff.id,
                "username": staff.username,
                "email": staff.email,
                "company": company.name,
                "role": role.name
            },
            "status": 201
        })

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
            return Response({"msg": "Missing required fields", "status": 400})

        if Role.objects.filter(name=name, company_id=company_id, deleted=False).exists():
            return Response({"msg": "Role already exists", "status": 400})

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({"msg": "Company not found", "status": 404})

        role = Role.objects.create(name=name, description=description, company=company)

        for perm in module_permissions_data:
            module_id = perm.get("module_id")
            if not module_id:
                return Response({"msg": "Module ID is required in permissions"}, status=400)

            try:
                module = Module.objects.get(id=module_id)
            except Module.DoesNotExist:
                return Response({"msg": f"Module with ID {module_id} does not exist"}, status=400)

            ModulePermission.objects.create(
                job_role=role,
                company=company,
                module=module,
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
                "status": 403
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
            return Response({"msg": "Missing required fields", "status": 400})

        try:
            role = Role.objects.get(id=role_id, company_id=company_id, deleted=False)
        except Role.DoesNotExist:
            return Response({"msg": "Role not found", "status": 404})

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({"msg": "Company not found", "status": 404})

        with transaction.atomic():
            role.name = name
            role.description = description
            role.save()

            # Delete old module permissions for this role
            ModulePermission.objects.filter(job_role=role).delete()

            for mod_perm in module_permissions:
                module_name = mod_perm.get("module_name")
                try:
                    module = Module.objects.get(name=module_name)
                except Module.DoesNotExist:
                    return Response({"msg": f"Module '{module_name}' not found", "status": 400})

                ModulePermission.objects.create(
                    job_role=role,
                    company=company,
                    module_name=module.name,
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
            return Response({"msg": "Role not found", "status": 404})

        #  Only allow deletion if the role belongs to the user's company
        if hasattr(request.user, 'company_id') and role.company_id != request.user.company_id:
            return Response({"msg": "Unauthorized to delete this role", "status": 403})

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

    
# class ListAllPermissionsView(APIView):
#     permission_classes =[IsAuthenticated, IsCompanyAdminOrAssigned]
#    

#     def get(self, request):
#         permissions = CustomPermission.objects.all()
#         data = [
#             {
#                 "id": p.id,
#                 "code": p.code,
#                 "description": p.description
#             }
#             for p in permissions
#         ]
#         return Response({
#             "msg": "Permissions fetched successfully",
#             "data": data,
#             "status": 200
#         })


# class AssignRoleToStaffView(APIView):
#     permission_classes =[IsAuthenticated, IsCompanyAdminOrAssigned]
#    

#     def put(self, request, company_id, pk):
#         role_id = request.data.get('role_id')
#         if not role_id:
#             return Response({"msg": "role_id is required", "status": 400})

#         try:
#             staff = StaffProfile.objects.get(pk=pk, company_id=company_id, is_active=True)
#         except StaffProfile.DoesNotExist:
#             return Response({"msg": "Staff not found in this company", "status": 404})

#         try:
#             role = Role.objects.get(id=role_id, company_id=company_id, deleted=False)
#         except Role.DoesNotExist:
#             return Response({"msg": "Role not found in this company", "status": 404})

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