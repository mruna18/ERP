from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Company
from .serializers import CompanySerializer
from customer.models import Customer

class CompanyCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            customer = Customer.objects.get(user=user)
        except Customer.DoesNotExist:
            return Response({"error": "Customer profile not found"}, status=404)

        if Company.objects.filter(user=user).count() >= customer.company_limit:
            return Response({"error": "Company limit reached"}, status=403)

        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
