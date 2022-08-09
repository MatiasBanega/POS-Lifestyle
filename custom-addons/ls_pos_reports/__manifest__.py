{
    'name': 'Reports',
    'version': '1.1',
    'category': 'Point of Sale Reports',
    'summary': 'User-friendly PoS interface for shops and restaurants',
    'description': "",
    'depends': ['base','lifestyle_masters'],
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
        
    ],

    
    
    'installable': True,
    'auto_install': False
}
