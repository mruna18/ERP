from staff.models import *
from companies.models import *

DEFAULT_PERMISSIONS = [
    # Invoice
    {"code": "create_invoice", "description": "Can create invoice"},
    {"code": "view_invoice", "description": "Can view invoice"},
    {"code": "edit_invoice", "description": "Can edit invoice"},
    {"code": "delete_invoice", "description": "Can delete invoice"},

    # Party
    {"code": "create_party", "description": "Can create party"},
    {"code": "edit_party", "description": "Can edit party"},
    {"code": "delete_party", "description": "Can delete party"},
    {"code": "view_party", "description": "Can view party"},

    # Staff & Roles
    {"code": "manage_staff", "description": "Can manage staff"},
    {"code": "manage_roles", "description": "Can manage roles and permissions"},

    # Items
    {"code": "create_item", "description": "Can create item"},
    {"code": "edit_item", "description": "Can edit item"},
    {"code": "delete_item", "description": "Can delete item"},
    {"code": "view_item", "description": "Can view item"},

    # Company & Settings
    {"code": "view_company", "description": "Can view company settings"},
    {"code": "edit_company", "description": "Can edit company settings"},
    {"code": "delete_company", "description": "Can delete company settings"},
    {"code": "create_company", "description": "Can create company settings"},

    # Reports
    {"code": "view_reports", "description": "Can view reports"},
    {"code": "export_reports", "description": "Can export reports to Excel/PDF"},

    # Dashboard
    {"code": "view_dashboard", "description": "Can view dashboard"},

    # Payments & Ledger
    {"code": "create_payment", "description": "Can create payment entry"},
    {"code": "view_ledger", "description": "Can view ledger"},
    {"code": "edit_ledger", "description": "Can edit ledger entries"},

    # Bank & Cash
    {"code": "manage_bank", "description": "Can manage bank accounts"},
    {"code": "manage_cash", "description": "Can manage cash ledger"},
    {"code": "view_bank_transfer", "description": "Can view bank-to-bank transfers"},
    {"code": "create_bank_transfer", "description": "Can create bank-to-bank transfer"},
    {"code": "delete_bank_transfer", "description": "Can delete bank-to-bank transfer"},

    #customer
    {"code": "view_customer", "description": "Can view customers"},
    {"code": "edit_customer", "description": "Can edit customer details"},
    {"code": "delete_customer", "description": "Can delete customers"},

]


def seed_roles():
    role_permission_map = {
        "Admin": [
            "create_invoice", "view_invoice", "edit_invoice", "delete_invoice",
            "create_party", "edit_party", "delete_party", "view_party",
            "manage_staff", "view_dashboard"
        ],
        "Sales": [
            "create_invoice", "view_invoice", "edit_invoice", "view_party"
        ],
        "Accountant": [
            "view_invoice", "view_party", "view_dashboard"
        ]
    }

    all_companies = Company.objects.filter(deleted=False)  # Optional: skip deleted companies

    for company in all_companies:
        print(f"\n🏢 Company: {company.name} (ID: {company.id})")
        for role_name, perm_codes in role_permission_map.items():
            role, created = Role.objects.get_or_create(
                name=role_name,
                company=company,
                defaults={"description": f"{role_name} role for {company.name}"}
            )

            if created:
                print(f"✅ Created role: {role_name}")
            else:
                print(f"✔️ Role already exists: {role_name}")

            # Assign permissions
            perms = CustomPermission.objects.filter(code__in=perm_codes)
            role.permissions.set(perms)
            print(f"🔗 Linked {len(perms)} permissions to role {role_name}")

    print("\n✅ All roles and permissions seeded across companies.")


def seed_permissions():
    for perm in DEFAULT_PERMISSIONS:
        obj, created = CustomPermission.objects.get_or_create(code=perm["code"], defaults={"description": perm["description"]})
        if created:
            print(f"✅ Created: {perm['code']}")
        else:
            print(f"✔️ Already exists: {perm['code']}")
