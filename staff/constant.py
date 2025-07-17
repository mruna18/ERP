# staff/constants.py

DEFAULT_ROLES = {
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
