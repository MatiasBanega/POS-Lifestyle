# -*- coding: utf-8 -*-
 
from datetime import datetime, timedelta
 
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

DATE_FORMAT = "%d-%m-%y"
DATE_FORMAT_2 = "%d/%m/%y"
DATE_FORMAT_3 = "%d/%m/%y"
 
class SalesOpenOrdersDetailsReport(models.AbstractModel):    
    _name = 'report.ls_pos_reports.report_summary'
 
    #@api.model
    def _get_report_values(self, docids, data=None):
        start_date = data['form']['start_date'] 
        end_date = data['form']['end_date']
        
        sql='''
          select to_char(date,'dd/mm/yyyy') as date,pos,cashier,sale_amount,cash,
                    ccard,voucher,sodexo,gift,lrvvoc,
                     phonepe,googlepay,loycoupon,parkingtkn,
                     giftpass,paytm,othercpn,ticket,txpress,
                     upipayment,razorpay,advpaid,cashdisc,
                     cr_sal,cr_disc,cashinhand ,ex_sh,bills from
                    sales_summary_screen_line         
                    where department_id=(select max(department_id) from sales_summary_screen_line)                                    
                  ''' 
                   
        self.env.cr.execute(sql) 
        emp_data = self.env.cr.dictfetchall()
        docs = []
        seq = 0
        for line in emp_data:  
            docs.append({            
                                    'date':line['date'],
                                    'pos' : line['pos'],
                                    'cashier' :line['cashier'],
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
                                    'advpaid': line['advpaid'],
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
            'end_date' :end_date,
            'company_id':company_id,
            'docs':docs,
            }
        
        

        
        