{
    'name': 'Hostel Allocation',
    'version': '18.1',  
    'license': 'AGPL-3',
    'category': 'Housing',
    'summary': 'Manage hostel allocations, rooms, and tenants',
    'description': """
        Hostel Allocation Module
        ============================
        This module allows you to:
        * Manage hostels with their details
        * Manage rooms and their statuses
        * Manage tenants and their allocations
        * Generate invoices for tenants
    """,
    'author': 'Anjana Sathian',
    'depends': ['base', 'mail'],
    'data': [
        'data/sequence.xml',
        'data/dashboard_data.xml',
        'data/tenant_email_template.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'report/hostel_invoice_template.xml',
        'report/hostel_invoice_report.xml',
        'views/category_views.xml',
        'views/dashboard_views.xml',
        'views/hostel_views.xml',
        'views/room_views.xml',
        'views/bed_views.xml',
        'views/tenant_views.xml',
        'views/invoice_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'hostel_allocation/static/src/scss/dashboard.scss',
            'hostel_allocation/static/src/js/tenant_control_panel.js',
            'hostel_allocation/static/src/xml/tenant_control_panel.xml',
        ],
    },

    'installable': True,
    'application': True,
}