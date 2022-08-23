# -*- coding: utf-8 -*-
{
    'name': 'SuperStore Report Forms',
    'version': '1.0',
    'author': "TenthPlanet",
    'website': "http://tenthplanet.in",
    'company': 'Master',
    'summary': 'SuperStore Report Forms',
    'description': """
        
""",
    'depends': ['base',],
    'data': [   
        'views/ss_report_forms_view.xml',
        'views/dept_wise_sales_view.xml',
        'views/inter_branch_transfer_views.xml',
        'views/purchase_detail_report_gst_view.xml',
        'views/total_sales_view.xml',
        'views/cashier_wise_sales_view.xml',
        'views/summary_sales_view.xml',
        'views/ss_cancel_bill_view.xml',
        'views/ss_stock_adjust_formview.xml',
        'views/ss_pos_exchange_form.xml',
        'views/bill_count_form_ss.xml',
        'views/purchase_report_view.xml',
        'security/ir.model.access.csv',
     ],
    'installable': True,
    'auto_install': False,
}
