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
    'depends': ['base'],
    'data': [
        'data/sequence.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hostel_views.xml',
        'views/room_views.xml',
        'views/bed_views.xml',
        'views/menu_views.xml',
    ],
    
    'installable': True,
    'application': True,
}