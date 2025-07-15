from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from staff.models import StaffProfile, Role
from companies.models import Company  
from django.db import transaction

class CreateStaffView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data

        required_fields = ['username', 'email', 'password', 'role_id', 'company_id']
        for field in required_fields:
            if not data.get(field):
                return Response({"status": 400, "message": f"{field} is required."}, status=400)

        username = data['username']
        email = data['email']
        password = data['password']
        role_id = data['role_id']
        company_id = data['company_id']

        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response({"status": 404, "message": "Role not found."}, status=404)

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({"status": 404, "message": "Company not found."}, status=404)

        with transaction.atomic():
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                return Response({"status": 400, "message": "Username already exists."}, status=400)

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # Create staff profile
            staff = StaffProfile.objects.create(
                user=user,
                role=role,
                company=company,
                is_active=True
            )

        return Response({
            "status": 201,
            "message": "Staff user created successfully.",
            "data": {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "role": role.name,
                "company": company.name,
                "staff_id": staff.id
            }
        }, status=201)
