{
    'name': 'Carafewerk',
    'version': '1.2',
    'summary': 'Module for Carafewerk',
    'sequence': -100,
    'description': 'A custom module for managing Carafewerk.',
    'author': 'Carafewerk',
    'category': 'website',
    'website': 'https://www.odoo.com/app/invoicing',
    'depends': ['base', 'website'],
    'data': [
        'security/ir.model.access.csv',

    ],
    'assets': {
        'web.assets_frontend': [
            'web/static/src/css/carafewerk.css',
            'web/static/src/images/*',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
