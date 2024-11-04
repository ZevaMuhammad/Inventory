{
    'name': 'Inventory Management',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Advanced Inventory Management System',
    'description': """
        This module provides advanced inventory management capabilities including:
        * Product management
        * Warehouse management
        * Stock locations
        * Stock movements
        * Reorder alerts
        * Inventory reports
        * Real-time dashboard
    """,
    'author': 'Zeva',
    'website': 'https://www.yourwebsite.com',
    'depends': [
        'base',
        'mail',
        'report_xlsx',
        'auth_api_key',
        'stock'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/product_views.xml',
        'views/warehouse_views.xml',
        'views/stock_location_views.xml',
        'views/stock_move_views.xml',
        'views/reorder_alert_views.xml',
        'views/report_views.xml',
        'views/dashboard_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'inventory/static/src/js/dashboard.js',
            'inventory/static/src/css/dashboard.css',
        ],
        'web.assets_qweb': [
            'inventory_management/static/src/xml/inventory_management_templates.xml',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}