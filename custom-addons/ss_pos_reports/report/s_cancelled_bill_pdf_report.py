from datetime import datetime, timedelta
 
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

 
class Super_CancelBillReport(models.AbstractModel):    
    _name = 'report.ss_pos_reports.super_report_cancelled'
 
    
    def _get_report_values(self, docids, data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        company_id = data['form']['company_id']


        
        sql = '''       
                select ss_bill_date,ss_bill_number,ss_uname,ss_pcode,ss_pname,ss_total_amt from
                    ss_bill_cancel_line         
                    where cancel_bill_id=(select max(cancel_bill_id) from ss_bill_cancel_line)
                                             
                '''
                
        self.env.cr.execute(sql) 
        ss_bill_data = self.env.cr.dictfetchall()
        docs = []
        seq = 0
        for line in ss_bill_data: 
             
            docs.append({ 
                                'ss_bill_date' : line['ss_bill_date'],
                                'ss_bill_number' : line['ss_bill_number'],
                                'ss_uname' : line['ss_uname'],
                                'ss_pcode' : line['ss_pcode'],
                                'ss_pname' : line['ss_pname'],
                                'ss_total_amt' : line['ss_total_amt'],
            })
                       
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'], 
            'start_date':start_date,
            'end_date':end_date,
            'company_id':company_id,
            'docs':docs,
            }
        
        

        
        