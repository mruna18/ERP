from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Item, UnitType
from .serializer import *
from customer.models import Customer
from companies.models import *
from staff.permission import *

from rest_framework import status

class ItemCreateView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Items"
    required_permission = "create"

    def post(self, request):
        company_id = request.data.get("company")
        if not company_id:
            return Response({"error": "'company' is required."}, status=status.HTTP_400_BAD_REQUEST)

        customer, company, error = get_user_context(request, company_id)
        if error:
            return error

        serializer = ItemSerializer(data=request.data)
        if not serializer.is_valid():
            error_messages = [f"{field}: {error[0]}" for field, error in serializer.errors.items()]
            return Response({"error": " | ".join(error_messages)}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Safely parse numeric fields
        try:
            price = float(data.get("price", 0))
            sales_price = float(data.get("sales_price", 0))
            tax_applied = data.get("tax_applied", False)
            tax_percent = float(data.get("tax_percent", 0))
        except (TypeError, ValueError):
            return Response({"error": "Invalid data type in numeric fields."}, status=status.HTTP_400_BAD_REQUEST)

        if price > 1e7 or sales_price > 1e7:
            return Response({"error": "Price or Sales Price is too large."}, status=status.HTTP_400_BAD_REQUEST)

        # Final price calculation
        def apply_tax(base, tax):
            return round(base + (base * tax / 100), 2) if tax_applied else round(base, 2)

        final_price = apply_tax(price, tax_percent)
        final_sales_price = apply_tax(sales_price, tax_percent)

        with transaction.atomic():
            item = Item.objects.create(
                name=data["name"],
                code=data["code"],
                description=data.get("description", ""),
                quantity=data.get("quantity", 0),
                unit=data["unit"],
                price=final_price,
                sales_price=final_sales_price,
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
        }, status=status.HTTP_201_CREATED)



# list

class ListItemView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Items"
    required_permission = "get_using_post"

    def post(self, request):
        company_id = request.data.get("company")
        customer_id = request.data.get("customer_id")

        if not company_id or not customer_id:
            return Response({"detail": "customer_id and company are required."}, status=400)

        user, company, error = get_user_context(request, company_id)
        if error:
            return error

        if isinstance(user, Customer):
            if user.id != int(customer_id):
                return Response({"detail": "Customer ID mismatch."}, status=403)
        elif isinstance(user, StaffProfile):
            if user.company.id != int(company_id):
                return Response({"detail": "Unauthorized staff for this company."}, status=403)
        else:
            return Response({"detail": "Unauthorized user."}, status=403)

        items = Item.objects.filter(company=company, is_active=True)
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data, status=200)



class UnitTypeListView(APIView):
    """
    Simple list of all available units (global, not per-company).
    Auto-creates default units if none exist.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Auto-create default units if they don't exist
        default_units = [
            {"name": "Piece", "code": "pcs"},
            {"name": "Kilogram", "code": "kg"},
            {"name": "Gram", "code": "g"},
            {"name": "Liter", "code": "L"},
            {"name": "Meter", "code": "m"},
            {"name": "Box", "code": "box"},
            {"name": "Pack", "code": "pack"},
        ]
        
        for unit_data in default_units:
            UnitType.objects.get_or_create(
                name=unit_data["name"],
                defaults={"code": unit_data["code"]}
            )
        
        units = UnitType.objects.all().order_by("name")
        data = [
            {
                "id": unit.id,
                "name": unit.name,
                "code": unit.code,
            }
            for unit in units
        ]
        return Response(data, status=200)



# get by id
class RetrieveItemView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Items"
    required_permission = "can_view_specific"

    def get(self, request, company_id, pk):
        user, company, error = get_user_context(request, company_id)
        if error:
            return error

        try:
            item = Item.objects.get(pk=pk, company=company, is_active=True)
        except Item.DoesNotExist:
            return Response({"detail": "Item not found for this company."}, status=404)

        serializer = ItemSerializer(item)
        return Response(serializer.data, status=200)



# PUT /items/<int:company_id>/<int:pk>/
class UpdateItemView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Items"
    required_permission = "edit"

    def put(self, request, company_id, pk):
        customer, company, error = get_user_context(request, company_id)
        if error:
            return error

        try:
            item = Item.objects.get(pk=pk, company=company, is_active=True)
        except Item.DoesNotExist:
            return Response({"detail": "Item not found."}, status=404)

        serializer = ItemSerializer(instance=item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        price = float(data.get("price", item.price))
        sales_price = float(data.get("sales_price", item.sales_price))
        tax_applied = data.get("tax_applied", item.tax_applied)
        tax_percent = float(data.get("tax_percent", item.tax_percent))

        if tax_applied:
            price += price * (tax_percent / 100)
            sales_price += sales_price * (tax_percent / 100)

        with transaction.atomic():
            for field in ["name", "code", "description", "quantity", "unit"]:
                setattr(item, field, data.get(field, getattr(item, field)))

            item.price = round(price, 2)
            item.sales_price = round(sales_price, 2)
            item.tax_applied = tax_applied
            item.tax_percent = round(tax_percent, 2)
            item.save()

        return Response({"msg": "Item updated successfully."}, status=200)

# DELETE /items/<int:company_id>/<int:pk>/
class DeleteItemView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned, HasModulePermission]
    required_module = "Items"
    required_permission = "delete"

    def delete(self, request, company_id, pk):
        customer, company, error = get_user_context(request, company_id)
        if error:
            return error

        try:
            item = Item.objects.get(pk=pk, company=company, is_active=True)
        except Item.DoesNotExist:
            return Response({"detail": "Item not found."}, status=404)

        item.is_active = False
        item.save()
        return Response({"msg": "Item soft-deleted successfully."}, status=204)
