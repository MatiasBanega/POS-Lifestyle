# -*- coding: utf-8 -*-
 
from datetime import datetime, timedelta
 
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

DATE_FORMAT = "%d-%m-%y"
DATE_FORMAT_2 = "%d/%m/%y"
DATE_FORMAT_3 = "%d/%m/%y"
 
class deptwisereport(models.AbstractModel):    
    _name = 'report.ls_pos_reports.report_dept_wise'
 
    #@api.model
    def _get_report_values(self, docids, data=None):
        start_date = data['form']['start_date'] 
        end_date = data['form']['end_date'] 
        company_id = data['form']['company_id']

        
        sql='''
                 select department,tax ,tax_amt,cgst,sgst,cessamt,mark_down,total from
                    dept_wise_sales_line         
                    where deptsale_id=(select max(deptsale_id) from dept_wise_sales_line)
                               
                  '''# % ((start_date),(start_date))
                
                
        self.env.cr.execute(sql) 
        emp_data = self.env.cr.dictfetchall()
        sum_amt = 0
        tot_qty = 0
        docs = []
        total_pdf = []
        seq = 0
        for line in emp_data: 
#             if line['sold_qty']:
#                 tot_qty+=line['sold_qty'] 
#             if line['sold_value']:
#                 sum_amt+=line['sold_value']
            docs.append({ 
                                'department' : line['department'],
                                'tax' : line['tax'],
                                'tax_amt' : line['tax_amt'],
                                'cgst' : line['cgst'],  
                                'sgst' : line['sgst'],
                                'cessamt' : line['cessamt'],
                                'mark_down' : line['mark_down'],
                                'total' : line['total'],  
            })

        #print(sum_amt)
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'], 
            'start_date':start_date,  
            'end_date':end_date,
            'company_id':company_id,
            'docs':docs,
            }
        
        

        
        