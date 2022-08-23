from odoo import models, fields

 
class SummarySalesDetailsReport(models.AbstractModel):    
    _name = 'report.ss_pos_reports.report_summary'
 
  
    def _get_report_values(self, docids, data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        company_id = data['form']['company_id']     

        
        sql = ''' 
               select date,pos,sale_amount,cash,
                    ccard,voucher,sodexo,gift,lrvvoc,
                     phonepe,googlepay,loycoupon,parkingtkn,
                     giftpass,paytm,othercpn,ticket,txpress,
                     upipayment,razorpay,cashdisc,
                     cr_sal,cr_disc,cashinhand ,ex_sh,bills from summary_sales_report_screen_line_ss 
                     where summary_order_id=(select max(summary_order_id) from summary_sales_report_screen_line_ss)
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
                                    'date':line['date'],
                                    'pos' : line['pos'],
                                    'sale_amount' :line['sale_amount'],
                                    'cash' : line['cash'],
                                    'ccard' :line['ccard'],
                                    'voucher' :line['voucher'],
                                    'sodexo' : line['sodexo'],
                                    'gift' : line['gift'],
                                    'lrvvoc': line['lrvvoc'],
                                    'phonepe' : line['phonepe'],
                                    'googlepay' :line['googlepay'], 
                                    'loycoupon' :line['loycoupon'],
                                    'parkingtkn' : line['parkingtkn'],
                                    'giftpass' : line['giftpass'],
                                    'paytm': line['paytm'],
                                    'othercpn': line['othercpn'],
                                    'ticket' : line['ticket'],
                                    'txpress' : line['txpress'],
                                    'upipayment' : line['upipayment'],
                                    'razorpay' : line['razorpay'],
                                    'cashdisc' : line['cashdisc'] , 
                                    'cr_sal' : line['cr_sal'],
                                    'cr_disc' : line['cr_disc'],
                                    'cashinhand': line['cashinhand'],
                                    'ex_sh' : line['ex_sh'],
                                    'bills': line['bills'],
          
                                                         

            })
                       
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'start_date':start_date,
            'end_date':end_date,
            'company_id':company_id,
            'docs':docs,
            }
        

        
        