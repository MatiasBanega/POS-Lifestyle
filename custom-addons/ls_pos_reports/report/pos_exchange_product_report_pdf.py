# -*- coding: utf-8 -*-
 
from datetime import datetime, timedelta
 
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

DATE_FORMAT = "%d-%m-%y"
DATE_FORMAT_2 = "%d/%m/%y"
DATE_FORMAT_3 = "%d/%m/%y"
 
class posreport(models.AbstractModel):    
    _name = 'report.ls_pos_reports.pos_exchange_report'
 
    #@api.model
    def _get_report_values(self, docids, data=None):
        start_date = data['form']['start_date'] 
        end_date = data['form']['end_date']
        cashier_id = data['form']['cashier_id']
        is_unusedbill = data['form']['is_unusedbill']
        company_id = data['form']['company_id']

        
        sql='''
               select exchange_bill,original_bill ,invoice_date,product_code,product_name,brand,item_type,product_design
                 ,product_color,product_size,exchange_qty,original_billsp,line_total,balance_amt,cashier,terminal,
                 sales_rep from
                    pos_exchange_product_screen_line         
                    where pos_id=(select max(pos_id) from pos_exchange_product_screen_line)   
                               
                  '''
                
                
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
                                'brand' : line['brand'],
                                'item_type' :line['item_type'],
                                'product_design' : line['product_design'],
                                'product_color' : line['product_color'],
                                'product_size' : line['product_size'],
                                'exchange_qty' : line['exchange_qty'],
                                'original_billsp' : line['original_billsp'],
                                'line_total' : line['line_total'],
                                'balance_amt' : line['balance_amt'],
                                'cashier' : line['cashier'],
                                'terminal' : line['terminal'],
                                'sales_rep' : line['sales_rep']})

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'], 
            'start_date':start_date,
            'end_date':end_date,
            'cashier_id':cashier_id.name,
            'is_unusedbill':is_unusedbill,
            'company_id':company_id,
            'docs':docs,
            }
        
        

        
        