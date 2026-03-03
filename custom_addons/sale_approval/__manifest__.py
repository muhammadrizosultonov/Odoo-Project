{
    "name": "Sale Approval",
    "summary": "Yirik summali savdo buyurtmalari uchun approval jarayoni",
    "version": "17.0.1.0.0",
    "category": "Sales/Sales",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": ["sale_management"],
    "data": [
        "security/sale_approval_security.xml",
        "security/ir.model.access.csv",
        "data/sale_approval_sequence.xml",
        "views/sale_approval_request_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "application": False,
}
