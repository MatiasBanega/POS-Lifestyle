# -*- coding: utf-8 -*-
{
    'name': 'Lifestyle Database Connection',
    'version': '1.0',
    'author': "TenthPlanet",
    'website': "http://tenthplanet.in",
    'category': 'Sales',
    'summary': 'Lifestyle Database Connection',
    'description': """
        
""",
    'depends': ['base','mail','lifestyle_masters'],
    'data': [   
        'views/db_connection_views.xml',
        'security/ir.model.access.csv',
     ],
    'installable': True,
    'auto_install': False,
}
