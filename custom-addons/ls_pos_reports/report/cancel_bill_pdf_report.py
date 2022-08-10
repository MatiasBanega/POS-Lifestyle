from datetime import datetime, timedelta
 
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

 
class CancelBillReport(models.AbstractModel):    
    _name = 'report.ls_pos_reports.report_cancelled'
 
    
    def _get_report_values(self, docids, data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        company_id = data['form']['company_id']

        
        sql = '''       
                select bill_date,bill_number,uname,pcode,pname,total_amt from
                    bill_cancel_line         
                    where cancel_id=(select max(cancel_id) from bill_cancel_line)
                                               
                '''
                
        self.env.cr.execute(sql) 
        cbill_data = self.env.cr.dictfetchall()
        docs = []
        seq = 0
        for line in cbill_data: 
             
            docs.append({ 
                                'bill_date' : line['bill_date'],
                                'bill_number' : line['bill_number'],
                                'uname' : line['uname'],
                                'pcode' : line['pcode'],
                                'pname' : line['pname'],
                                'total_amt' : line['total_amt'],
            })
                       
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'], 
            'start_date':start_date,
            'end_date':end_date,
            'company_id':company_id,
            'docs':docs,
            }
        
        

        
        