# -*- coding: utf-8 -*-
 
from datetime import datetime, timedelta
 
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

 
class BillDetailsReport(models.AbstractModel):    
    _name = 'report.ls_pos_reports.billcount'
 
    #@api.model
    def _get_report_values(self, docids, data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        company_id = data['form']['company_id']

        
        sql = '''       
            select terminal,startno ,endno,totalbillcount,oflinecnt,onlinecnt,cancelcount from
                    billno_count_line         
                    where bill_id=(select max(bill_id) from billno_count_line)   
             '''
        
        self.env.cr.execute(sql)

        count_data = self.env.cr.dictfetchall()
        docs = []
        seq = 0
        for line in count_data:

            seq += 1
            today = fields.Date.today()
            todaydate = fields.Date.from_string(today)

            daysdue = ''

            docs.append({
                                'terminal' : line['terminal'],
                                'startno' : line['startno'],
                                'endno' : line['endno'],
                                'totalbillcount' : line['totalbillcount'],
                                'onlinecnt' : line['onlinecnt'],
                                'oflinecnt' : line['oflinecnt'],
                                'cancelcount' : line['cancelcount'],
            })
                       
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'start_date':start_date,
            'end_date':end_date, 
            'company_id':company_id,
            'docs':docs,
            }
        
        

        
        