# -*- coding: utf-8 -*-
{
    'name': 'LifeStyle Report Forms',
    'version': '1.0',
    'author': "TenthPlanet",
    'website': "http://tenthplanet.in",
    'company': 'Master',
    'summary': 'LifeStyle Report Forms',
    'description': """
        
""",
    'depends': ['base','ls_pos_reports'],
    'data': [   
        'views/ls_report_forms_view.xml',
        'views/dept_wise_sales_view.xml',
        'views/pos_product_wise_exchange_view.xml',
        'views/purchase_detail_report_gst_view.xml',
        'views/total_sales_view.xml',
        'views/bill_count_view.xml',
        'views/cancel_bill_view.xml',
        'views/summary_sales_view.xml',
        'views/cashier_wise_sales_view.xml',
        'views/stock_adjust_form_view.xml',
         'views/inter_branch_form_view.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
     ],
    'installable': True,
    'auto_install': False,
}
