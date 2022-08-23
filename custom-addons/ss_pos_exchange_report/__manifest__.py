# -*- coding: utf-8 -*-
{
    'name': 'SS POS Custom Report',
    'version': '1.0',
    'author': "TenthPlanet",
    'website': "http://tenthplanet.in",
    'category': 'Sales',
    'summary': 'POS Custom Report',
    'description': """
        
""",
    'depends': ['base','sale','account','point_of_sale','product'],
    'data': [   
  
        'views/ss_pos_product_wise_exchange_report_excel.xml',
        'views/ss_pos_product_wise_exchange_report_pdf.xml',
        'security/ir.model.access.csv',
       
       
     ],

    'installable': True,
    'auto_install': False,
}
