from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Item
from .serializer import *
from customer.models import Customer
from companies.models import Company

class ItemCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        customer_id = request.data.get("customer_id")
        company_id = request.data.get("company")

        # Check for required fields
        if not customer_id:
            return Response({"error": "Customer ID is required."}, status=400)
        if not company_id:
            return Response({"error": "Company ID is required."}, status=400)

        # Validate customer and company
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=404)

        try:
            company = Company.objects.get(id=company_id, owner=customer, is_active=True)
        except Company.DoesNotExist:
            return Response({"error": "Company not found or doesn't belong to this customer."}, status=404)

        # Extract and validate fields
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
            unit_type = data.get("unit")  # assuming unit is FK now
        except (TypeError, ValueError):
            return Response({"error": "Invalid input type for numeric fields."}, status=400)

        if price > 1e7 or sales_price > 1e7:
            return Response({"error": "Price or Sales Price is too large."}, status=400)

        # Calculate final prices
        final_price = price + (price * tax_percent / 100) if tax_applied else price
        final_sales_price = sales_price + (sales_price * tax_percent / 100) if tax_applied else sales_price

        # Save item
        with transaction.atomic():
            item = Item.objects.create(
                name=name,
                code=code,
                description=description,
                quantity=quantity,
                price=round(final_price, 2),
                sales_price=round(final_sales_price, 2),
                tax_applied=tax_applied,
                tax_percent=round(tax_percent, 2),
                unit=unit_type,
                company=company,
                created_by=request.user,
                is_active=True
            )

        return Response({"msg": "Item created successfully", "id": item.id}, status=status.HTTP_201_CREATED)


# list

class ListItemView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # customer = Customer.objects.filter(user=request.user,is_active=True).first()
        customer = Customer.objects.filter(user=request.user,is_active=True)

        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            return Response({"detail": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if not customer or not customer.selected_company:
            return Response({"detail": "Customer or selected company not found."}, status=status.HTTP_400_BAD_REQUEST)

        items = Item.objects.filter(company=customer.selected_company, is_active=True)
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# get by id
class RetrieveItemView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        customer = Customer.objects.filter(user=request.user).first()
        print(customer)
        if not customer or not customer.selected_company:
            return Response({"detail": "Customer or selected company not found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = Item.objects.get(pk=pk, company=customer.selected_company, is_active=True)
        except Item.DoesNotExist:
            return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)


# put
class UpdateItemView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        customer = Customer.objects.filter(user=request.user).first()
        if not customer or not customer.selected_company:
            return Response({"detail": "Customer or selected company not found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = Item.objects.get(pk=pk, company=customer.selected_company, is_active=True)
        except Item.DoesNotExist:
            return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

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

        return Response({"msg": "Item updated"}, status=status.HTTP_200_OK)



# delete
class DeleteItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        customer = Customer.objects.filter(user=request.user).first()
        if not customer or not customer.selected_company:
            return Response({"detail": "Customer or selected company not found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = Item.objects.get(pk=pk, company=customer.selected_company, is_active=True)
        except Item.DoesNotExist:
            return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

        item.is_active = False
        item.save()
        return Response({"msg": "Item soft-deleted."}, status=status.HTTP_204_NO_CONTENT)