from odoo import models

 
class totalsalesreport(models.AbstractModel): 
    _name = 'report.ls_pos_reports.report_total_sales'
 
    def _get_report_values(self, docids, data=None):
        start_date = data['form']['start_date'] 
        end_date = data['form']['end_date'] 
        company_id = data['form']['company_id'] 
        online_sales = data['form']['online_sales']
        
        sql = '''
            select datetrx,total_sales_amt,dis_amt,round_off,tot_net_amt,bill_count,avg_bill 
                from total_sales_line         
                where deptsale_id=(select max(deptsale_id) from total_sales_line)          
            '''               
                
        self.env.cr.execute(sql) 
        emp_data = self.env.cr.dictfetchall()
        docs = []
        for line in emp_data: 
            docs.append({
                'datetrx': line['datetrx'],
                'total_sales_amt': line['total_sales_amt'],
                'dis_amt': line['dis_amt'],
                'round_off': line['round_off'],
                'tot_net_amt': line['tot_net_amt'],
                'bill_count': line['bill_count'],
                'avg_bill': line['avg_bill'],
                     })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'start_date':start_date,
            'end_date':end_date,
            'company_id':company_id,
            'online_sales':online_sales,
            'docs':docs,
            }
        
        
