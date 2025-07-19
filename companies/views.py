from .models import *
from .serializers import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q,F,FloatField

from companies.models import *
from customer.models import *
from companies.serializers import *
import re
from staff.models import *
from staff.management.commands.seed_permissions import *
from staff.permission import *
from staff.constant import *
from staff.models import *
from invoice.models import *
from payments.models import *
from items.models import *


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return Customer.objects.filter(user=request.user).exists()
class CreateCompanyView(APIView):
    permission_classes =[IsAuthenticated,IsCustomer]

    def post(self, request):
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            return Response({"error": "Customer profile not found"}, status=404)

        if customer.companies.count() >= customer.company_limit:
            return Response({"error": "Company creation limit reached"}, status=403)

        company_name = request.data.get('name')
        gst_number = request.data.get('gst_number')
        phone = request.data.get('phone')

        if not company_name:
            return Response({"error": "Company name is required."}, status=400)
        if not gst_number:
            return Response({"error": "GST number is required."}, status=400)
        if not phone:
            return Response({"error": "Phone number is required."}, status=400)
        if not re.fullmatch(r"\d{10}", phone):
            return Response({"error": "Phone number must be exactly 10 digits."}, status=400)

        if Company.objects.filter(phone=phone, owner=customer, is_active=True).exists():
            return Response({"error": "Company with this phone already exists."}, status=400)
        if Company.objects.filter(gst_number=gst_number, owner=customer, is_active=True).exists():
            return Response({"error": "Company with this GST number already exists."}, status=400)
        if Company.objects.filter(name=company_name, gst_number=gst_number, owner=customer, is_active=True).exists():
            return Response({"error": "Company with same name and GST already exists for this user"}, status=400)

        # Create the company
        company = Company.objects.create(
            name=company_name,
            gst_number=gst_number,
            phone=phone,
            address=request.data.get('address', ''),
            user=request.user,
            owner=customer,
        )

        # Assign default roles and permissions
        # from staff.constant import DEFAULT_ROLES
        # for role_name, permission_codes in DEFAULT_ROLES.items():
        #     role, created = Role.objects.get_or_create(name=role_name, company=company)
        #     for code in permission_codes:
        #         permission = CustomPermission.objects.filter(code=code).first()
        #         if permission:
        #             role.permissions.add(permission)

        # Assign Admin role to the creator
        admin_role = Role.objects.filter(company=company, name="Admin").first()
        if admin_role:
            StaffProfile.objects.create(
                company=company,
                user=request.user,
                role=admin_role,
                is_active=True
            )

        return Response({
            "msg": "Company created successfully",
            "company_id": company.id,
            "name": company.name
        }, status=201)


# Helper function to get logged-in customer
def get_customer(user):
    try:
        return Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        return None
    


class CompanyListView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]
   
    
    def get(self, request):
        customer = get_customer(request.user)
        if not customer:
            return Response({'error': 'Customer not found'}, status=404)

        companies = Company.objects.filter(owner=customer, is_active=True)
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data)


class CompanyDetailView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned]
   

    def get(self, request, pk):
        customer = get_customer(request.user)
        try:
            company = Company.objects.get(pk=pk, owner=customer)
            serializer = CompanySerializer(company)
            return Response(serializer.data)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=404)


class CompanyUpdateView(APIView):
    permission_classes =[IsAuthenticated, IsCompanyAdminOrAssigned]
  

    def put(self, request, pk):
        customer = get_customer(request.user)
        try:
            company = Company.objects.get(pk=pk, owner=customer)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=404)

        serializer = CompanySerializer(company, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Company updated successfully', 'data': serializer.data})
        return Response(serializer.errors, status=400)


class CompanyDeleteView(APIView):
    permission_classes =[IsAuthenticated, IsCompanyAdminOrAssigned]
   
    def delete(self, request, pk):
        customer = get_customer(request.user)
        try:
            company = Company.objects.get(pk=pk, owner=customer, is_active=True)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=404)

        company.is_active = False
        company.save()
        return Response({'msg': 'Company soft deleted successfully'}, status=204)



#! select the compnay
class SelectCompanyView(APIView):
    permission_classes =[IsAuthenticated, IsCompanyAdminOrAssigned]

    def post(self, request):
        company_id = request.data.get('company_id')
        customer = get_customer(request.user)
        if not customer:
            return Response({"error": "Customer not found"}, status=404)

        try:
            company = Company.objects.get(id=company_id, owner=customer, is_active=True)
        except Company.DoesNotExist:
            return Response({"error": "Company not found or inactive"}, status=404)

        customer.selected_company = company
        customer.save()
        return Response({"msg": f"{company.name} set as selected company."})


#! DASHBOARD

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdminOrAssigned]

    def get(self, request):
        company_id = get_company_id(request, self)
        if not company_id:
            return Response({"error": "Invalid company"}, status=400)

        today = timezone.now().date()

        # Invoice Stats
        total_sales = Invoice.objects.filter(company_id=company_id, invoice_type=1, is_deleted=False).count()
        total_purchases = Invoice.objects.filter(company_id=company_id, invoice_type=2, is_deleted=False).count()
        today_sales = Invoice.objects.filter(company_id=company_id, invoice_type=1, created_at__date=today, is_deleted=False).count()

        # Amounts
        total_received = Invoice.objects.filter(company_id=company_id, invoice_type=1).aggregate(
            total=Sum('amount_paid')
        )['total'] or 0

        total_paid = Invoice.objects.filter(company_id=company_id, invoice_type=2).aggregate(
            total=Sum('amount_paid')
        )['total'] or 0

        # Receivables & Advances from customers
        receivable_agg = Invoice.objects.filter(company_id=company_id, invoice_type=1).aggregate(
            due=Sum(F('total') - F('amount_paid'), output_field=FloatField())
        )
        receivable_due = receivable_agg['due'] or 0
        if receivable_due >= 0:
            receivables = receivable_due
            advance_from_customers = 0
        else:
            receivables = 0
            advance_from_customers = abs(receivable_due)

        advance_customers = (
            Invoice.objects.filter(company_id=company_id, invoice_type=1, is_deleted=False)
            .annotate(extra_paid=F('amount_paid') - F('total'))
            .filter(extra_paid__gt=0)
            .values('party_id', 'party__name')
            .annotate(total_advance=Sum('extra_paid'))
        )

        # Payables & Advances to suppliers
        payable_agg = Invoice.objects.filter(company_id=company_id, invoice_type=2).aggregate(
            due=Sum(F('total') - F('amount_paid'), output_field=FloatField())
        )
        payable_due = payable_agg['due'] or 0
        if payable_due >= 0:
            payables = payable_due
            advance_to_suppliers = 0
        else:
            payables = 0
            advance_to_suppliers = abs(payable_due)

        # Cash & Bank
        cash_balance = CashLedger.objects.filter(company_name_id=company_id).aggregate(
            balance=Sum('current_balance')
        )['balance'] or 0

        bank_balance = BankAccount.objects.filter(company_id=company_id).aggregate(
            balance=Sum('current_balance')
        )['balance'] or 0

        # Party-wise payables
        payable_parties = (
            Invoice.objects.filter(company_id=company_id, invoice_type=2, is_deleted=False)
            .values('party_id', 'party__name')
            .annotate(
                total_due=Sum(F('total') - F('amount_paid'), output_field=FloatField())
            )
            .filter(total_due__gt=0)
        )

        # Invoice-wise payables
        payable_invoices = (
            Invoice.objects.filter(company_id=company_id, invoice_type=2, is_deleted=False)
            .annotate(due_amount=F('total') - F('amount_paid'))
            .filter(due_amount__gt=0)
            .values(
                'id',
                'invoice_number',  # Ensure this field exists; otherwise, replace with 'id'
                'party__name',
                'total',
                'amount_paid',
                'due_amount',
                'created_at',
            )
        )

        return Response({
            "stats": {
                "total_sales": total_sales,
                "total_purchases": total_purchases,
                "today_sales": today_sales,
                "total_received": total_received,
                "total_paid": total_paid,
                "receivables": receivables,
                "advance_from_customers": advance_from_customers,
                "advance_customers":advance_customers,
                "payables": payables,
                "advance_to_suppliers": advance_to_suppliers,
                "cash_balance": cash_balance,
                "bank_balance": bank_balance,
                "payable_parties": payable_parties,
                "payable_invoices": list(payable_invoices),
            }
        })
