from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Item
from .serializer import *
from customer.models import Customer
from companies.models import *
from staff.permission import *

class ItemCreateView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Items" 
    required_permission = "create"
   

    def post(self, request):
        serializer = ItemSerializer(data=request.data)
        if not serializer.is_valid():
            error_messages = [f"{field}: {error[0]}" for field, error in serializer.errors.items()]
            return Response({"error": " | ".join(error_messages)}, status=400)

        company_id = request.data.get("company")
        if not company_id:
            return Response({"error": "'company' is required."}, status=400)

        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=404)

        try:
            company = Company.objects.get(id=company_id, is_active=True)
        except Company.DoesNotExist:
            return Response({"error": "Company not found."}, status=404)

        if company.owner != customer:
            return Response({"error": "Company does not belong to this customer."}, status=403)

        data = serializer.validated_data
        try:
            name = data.get("name")
            code = data.get("code")
            quantity = data.get("quantity", 0)
            description = data.get("description", "")
            price = float(data.get("price", 0))
            sales_price = float(data.get("sales_price", 0))
            tax_applied = data.get("tax_applied", False)
            tax_percent = float(data.get("tax_percent", 0))
            unit_type = data.get("unit")
        except (TypeError, ValueError):
            return Response({"error": "Invalid data type in numeric fields."}, status=400)

        if price > 1e7 or sales_price > 1e7:
            return Response({"error": "Price or Sales Price is too large."}, status=400)

        final_price = price + (price * tax_percent / 100) if tax_applied else price
        final_sales_price = sales_price + (sales_price * tax_percent / 100) if tax_applied else sales_price

        with transaction.atomic():
            item = Item.objects.create(
                name=name,
                code=code,
                description=description,
                quantity=quantity,
                unit=unit_type,
                price=round(final_price, 2),
                sales_price=round(final_sales_price, 2),
                tax_applied=tax_applied,
                tax_percent=round(tax_percent, 2),
                company=company,
                created_by=request.user,
                is_active=True
            )

        return Response({
            "message": "Item created successfully.",
            "item_id": item.id,
            "status": 200
        })


# list

class ListItemView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Items" 
    required_permission = "view"


    def post(self, request):
        customer_id = request.data.get("customer_id")
        company_id = request.data.get("company")

        if not customer_id or not company_id:
            return Response({"detail": "customer_id and company are required."}, status=status.HTTP_400_BAD_REQUEST)

        customer = Customer.objects.filter(id=customer_id, user=request.user, is_active=True).first()
        if not customer:
            return Response({"detail": "Customer not found or inactive."}, status=status.HTTP_404_NOT_FOUND)

        company = Company.objects.filter(id=company_id, is_active=True).first()
        if not company:
            return Response({"detail": "Company not found or inactive."}, status=status.HTTP_404_NOT_FOUND)

        items = Item.objects.filter(company=company, is_active=True)
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



# get by id
class RetrieveItemView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Items" 
    required_permission = "view"
 
    def get(self, request, company_id, pk):
        customer = Customer.objects.filter(user=request.user, is_active=True).first()
        if not customer:
            return Response({"detail": "Customer not found or inactive."}, status=status.HTTP_404_NOT_FOUND)

        try:
            company = Company.objects.get(id=company_id, owner=customer, is_active=True)
        except Company.DoesNotExist:
            return Response({"detail": "Company not found or not owned by this customer."}, status=status.HTTP_404_NOT_FOUND)

        try:
            item = Item.objects.get(pk=pk, company=company, is_active=True)
        except Item.DoesNotExist:
            return Response({"detail": "Item not found for this company."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)



# PUT /items/<int:company_id>/<int:pk>/
class UpdateItemView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Items" 
    required_permission = "update"
    

    def put(self, request, company_id, pk):
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            return Response({"detail": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            company = Company.objects.get(id=company_id, owner=customer, is_active=True)
        except Company.DoesNotExist:
            return Response({"detail": "Company not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)

        try:
            item = Item.objects.get(pk=pk, company=company, is_active=True)
        except Item.DoesNotExist:
            return Response({"detail": "Item not found for this company."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ItemSerializer(instance=item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            price = float(data.get("price", item.price))
            sales_price = float(data.get("sales_price", item.sales_price))
            tax_applied = data.get("tax_applied", item.tax_applied)
            tax_percent = float(data.get("tax_percent", item.tax_percent))
        except ValueError:
            return Response({"detail": "Price or tax values must be float-compatible."}, status=status.HTTP_400_BAD_REQUEST)

        if tax_applied:
            price += price * (tax_percent / 100)
            sales_price += sales_price * (tax_percent / 100)

        with transaction.atomic():
            item.name = data.get("name", item.name)
            item.code = data.get("code", item.code)
            item.description = data.get("description", item.description)
            item.quantity = data.get("quantity", item.quantity)
            item.unit = data.get("unit", item.unit)
            item.price = price
            item.sales_price = sales_price
            item.tax_applied = tax_applied
            item.tax_percent = tax_percent
            item.save()

        return Response({"msg": "Item updated successfully."}, status=status.HTTP_200_OK)


# DELETE /items/<int:company_id>/<int:pk>/
class DeleteItemView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Items" 
    required_permission = "delete"
    

    def delete(self, request, company_id, pk):
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            return Response({"detail": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            company = Company.objects.get(id=company_id, owner=customer, is_active=True)
        except Company.DoesNotExist:
            return Response({"detail": "Company not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)

        try:
            item = Item.objects.get(pk=pk, company=company, is_active=True)
        except Item.DoesNotExist:
            return Response({"detail": "Item not found for this company."}, status=status.HTTP_404_NOT_FOUND)

        item.is_active = False
        item.save()
        return Response({"msg": "Item soft-deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
