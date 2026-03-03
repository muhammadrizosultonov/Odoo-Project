{
    "name": "Customer Credit Control",
    "summary": "Mijoz kredit limitini nazorat qilish",
    "version": "17.0.1.0.0",
    "category": "Sales",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": ["sale_management", "account"],
    "data": [
        "security/credit_control_security.xml",
        "security/ir.model.access.csv",
        "data/customer_credit_control_data.xml",
        "views/customer_credit_limit_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "application": False,
}
