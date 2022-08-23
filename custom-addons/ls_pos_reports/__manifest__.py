{
    'name': 'Lifestyle Reports',
    'version': '1.1',
    'category': 'Point of Sale Reports',
    'summary': 'User-friendly PoS interface for shops and restaurants',
    'description': "",
    'depends': ['base','web_domain_field','lifestyle_masters'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/pos_report_views.xml', 
        'views/cancel_bill_excel_report_views.xml', 
        'views/cancel_bill_pdf_report_views.xml',  
        'views/bill_count_excel_report_views.xml', 
        'views/billno_count_pdf_report.xml',  
        'views/dept_wise_sales_report_excel.xml', 
        'views/dept_wise_sales_report_pdf.xml',  
        'views/purchase_detail_excel_report_views.xml', 
        'views/purchase_detail_pdf_report_views.xml', 
        'views/pos_product_wise_exchange_report_excel.xml', 
        'views/pos_product_wise_exchange_report_pdf.xml',   
        'views/total_sales_report_excel.xml', 
        'views/total_sales_report_pdf.xml', 
        'views/sales_summary_excel_report_views.xml',
        'views/sales_summary_pdf_report_views.xml',   
        'views/cashier_sales_excel_report_views.xml', 
        'views/cashier_sales_pdf_report_views.xml',  
        'views/inter_branch_transfer_pdf_report.xml', 
        'views/inter_branch_transfer_report.xml',  
        'views/stock_adjustment_excel_report_views.xml', 
        'views/stock_adjustment_pdf_report_views.xml',   
        
    ],

    
    
    'installable': True,
    'auto_install': False
}
