# -*- coding: utf-8 -*-
 
from datetime import datetime, timedelta
 
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

DATE_FORMAT = "%d-%m-%y"
DATE_FORMAT_2 = "%d/%m/%y"
DATE_FORMAT_3 = "%d/%m/%y"
 
class deptwisereport(models.AbstractModel):    
    _name = 'report.ss_pos_reports.ss_pos_exchange_report_temp'
 
    #@api.model
    def _get_report_values(self, docids, data=None):
        start_date = data['form']['start_date'] 
        end_date = data['form']['end_date']
        cashier_id = data['form']['cashier_id']
        organization_id = data['form']['organization_id']
#         is_unusedbill = data['form']['is_unusedbill']
        company_id = data['form']['company_id']

        
        sql='''
            select exchange_bill,original_bill ,invoice_date,product_code,
                product_name,return_qty,original_invoicesp,line_total,cashier,terminal
                from
                    ss_pos_exchange_product_screen_line         
                    where pos_id=(select max(pos_id) from ss_pos_exchange_product_screen_line)   
                               
                  '''# % ((start_date),(start_date))
                
                
        self.env.cr.execute(sql) 
        prod_data = self.env.cr.dictfetchall()
        sum_amt = 0
        tot_qty = 0
        docs = []
        total_pdf = []
        seq = 0
        for line in prod_data: 
          
            docs.append({ 
                                'exchange_bill' : line['exchange_bill'],
                                'original_bill' : line['original_bill'],
                                'invoice_date' : line['invoice_date'],
                                'product_code' : line['product_code'],
                                'product_name' : line['product_name'],
                            
                                'return_qty' : line['return_qty'],
                                'original_invoicesp' : line['original_invoicesp'],
                                'line_total' : line['line_total'],
#                                 'balance_amt' : line['balance_amt'],
                                'cashier' : line['cashier'],
                                'terminal' : line['terminal'],
                                })

        #print(sum_amt)
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'], 
            'start_date':start_date,
            'end_date':end_date,
            'cashier_id':cashier_id,
#             'is_unusedbill':is_unusedbill,
            'company_id':company_id,
            'organization_id':organization_id,
            'docs':docs,
            }
        
        

        
        