from odoo import models, fields

 
class CashierwiseSalesDetailsReport(models.AbstractModel):    
    _name = 'report.ls_pos_reports.report_sales_cashier_wise'
 
  
    def _get_report_values(self, docids, data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        company_id = data['form']['company_id']     

        
        sql = ''' 
                select date, name, tender_type, amt  from cashier_sales_report_screen_line
                where cashier_order_id=(select max(cashier_order_id) from cashier_sales_report_screen_line)    
      
             '''
        self.env.cr.execute(sql) 
        emp_data = self.env.cr.dictfetchall()
        docs = []
        seq = 0
        for line in emp_data:
            seq += 1
            today = fields.Date.today()
            todaydate = fields.Date.from_string(today)
            daysdue = ''

            docs.append({
                        'date' : line['date'],
                                'name' : line['name'],
                                'tender_type' : line['tender_type'],
                                'amt' : line['amt'],
                              

            })
                       
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'start_date':start_date,
            'end_date':end_date,
            'company_id':company_id,
            'docs':docs,
            }
        

        
        