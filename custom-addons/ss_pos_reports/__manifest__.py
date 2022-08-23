{
    'name': 'SuperStore Reports',
    'version': '1.1',
    'category': 'Point of Sale Reports',
    'summary': 'User-friendly PoS interface for shops and restaurants',
    'description': "",
    'depends': ['base','lifestyle_masters','web_domain_field','ss_report_forms'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/ss_pos_reports_views.xml', 
        'views/cashier_sales_excel_report_views_ss.xml', 
        'views/cashier_sales_pdf_report_views_ss.xml',  
        'views/s_cancelled_bill_excel_views.xml', 
        'views/s_cancelled_bill_pdf_views.xml',  
        'views/ss_dept_wise_sales_excel_rpt_views.xml', 
        'views/ss_dept_wise_sales_pdf_rpt.xml',  
        'views/ss_inter_branch_trans_excel_rpt.xml', 
        'views/ss_inter_branch_trans_pdf_rpt.xml', 
        'views/ss_purchase_detail_excel_report_views.xml', 
#         'views/ss_purchase_detail_pdf_report_views.xml',   
        'views/ss_stock_adjustment_excel_views.xml', 
        'views/ss_stock_adjustment_pdf_views.xml', 
        'views/ss_total_sales_excel_rpt_views.xml',
        'views/ss_total_sales_pdf_rpt_views.xml',  
        'views/summary_sales_excel_report_views_ss.xml',
        'views/summary_sales_pdf_report_views_ss.xml',    
        'views/ss_pos_product_wise_exchange_report_excel.xml',
        'views/ss_pos_product_wise_exchange_report_pdf.xml',     
        'views/ss_bill_count_report_excel.xml',
        'views/ss_bill_count_report_pdf.xml',     
        
    ],

    
    
    'installable': True,
    'auto_install': False
}
