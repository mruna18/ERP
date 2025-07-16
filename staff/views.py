from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from staff.models import *
from companies.models import Company  
from django.db import transaction
from .serializer import *
from .permission import *

class CreateStaffView(APIView):
    permission_classes = [IsAuthenticated]
    # permission_classes = [IsAuthenticated, HasCustomPermission]
    # required_permission = 'manage_roles'  

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
    permission_classes = [IsAuthenticated]
    # permission_classes = [IsAuthenticated, HasCustomPermission]
    # required_permission = 'manage_roles'

    def post(self, request):
        data = request.data
        name = data.get('name')
        description = data.get('description', '')
        company_id = data.get('company_id')
        permission_ids = data.get('permission_ids', [])

        if not name or not company_id:
            return Response({"msg": "Missing required fields", "status": 400})

        if Role.objects.filter(name=name, company_id=company_id, deleted=False).exists():
            return Response({"msg": "Role already exists", "status": 400})

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({"msg": "Company not found", "status": 404})

        role = Role.objects.create(name=name, description=description, company=company)

        if permission_ids:
            permissions = CustomPermission.objects.filter(id__in=permission_ids)
            role.permissions.set(permissions)

        return Response({
            "msg": "Role created successfully",
            "data": {
                "id": role.id,
                "name": role.name,
                "company": company.name,
                "permissions": [p.code for p in role.permissions.all()]
            },
            "status": 201
        })


    
class ListStaffRolesView(APIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            role = Role.objects.get(pk=pk, deleted=False)
        except Role.DoesNotExist:
            return Response({"msg": "Role not found", "status": 404})

        # Optional: Only allow updating if the role belongs to the user's company
        if hasattr(request.user, 'company_id') and role.company_id != request.user.company_id:
            return Response({"msg": "Unauthorized to update this role", "status": 403})

        new_name = request.data.get("name")
        if Role.objects.filter(name=new_name, company=role.company, deleted=False).exclude(id=pk).exists():
            return Response({
                "msg": "A role with this name already exists for this company.",
                "status": 400
            })

        serializer = StaffRoleSerializer(role, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "msg": "Role updated successfully",
                "data": serializer.data,
                "status": 200
            })

        return Response({
            "msg": "Validation error",
            "errors": serializer.errors,
            "status": 400
        })


class SoftDeleteStaffRoleView(APIView):
    permission_classes = [IsAuthenticated]

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



class UpdateRolePermissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        role_id = request.data.get('role_id')
        permission_ids = request.data.get('permission_ids', [])

        if not role_id or not isinstance(permission_ids, list):
            raise CustomApiException(400, "role_id and permission_ids are required.")

        try:
            role = Role.objects.get(id=role_id, deleted=False)
        except Role.DoesNotExist:
            raise CustomApiException(404, "Role not found.")

        # Validate permission IDs
        permissions = CustomPermission.objects.filter(id__in=permission_ids)
        if permissions.count() != len(permission_ids):
            raise CustomApiException(400, "One or more permission IDs are invalid.")

        role.permissions.set(permissions)

        return Response({
            "status": 200,
            "message": "Permissions updated successfully.",
            "role": role.name,
            "permissions": [p.code for p in permissions]
        })