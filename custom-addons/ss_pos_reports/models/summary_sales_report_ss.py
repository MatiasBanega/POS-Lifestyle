from datetime import datetime
from datetime import date 
from dateutil.relativedelta import relativedelta
from odoo.osv import osv
from odoo import api, fields, models
from odoo import exceptions, _
from odoo.exceptions import UserError, ValidationError
import xlwt
import io
import base64
import re
import xlsxwriter
from itertools import count
from email.policy import default
import psycopg2
import json

DATE_FORMAT_1 = "%Y-%d-%m"
DATE_FORMAT_2 = "%d/%m/%y"
DATE_FORMAT_3 = "%m/%d/%y"


class summary_sales_details_wzd(models.Model):
    _name = "summary.sales.report.ss"
       
    start_date = fields.Date('Date From') 
    end_date = fields.Date(string="Date To") 
    company_id = fields.Many2one('res.company',string='Company',default=lambda self:self.env.company.id)
             
    def print_summary_sales_report(self):

        def get_summary_lines(self):
            res = {}
            dict={}
            lis=[]
            start_date = self.start_date
            end_date = self.end_date
            company_id=self.company_id.name
            
            try:
                db_conn = self.env['db.connection'].search([('company_id','=',self.company_id.name)], limit=1)
                db_connect=db_conn.database_connect()
                cursor = db_connect.cursor() 
                self.env['summary.sales.report.screen.line.ss'].search([]).unlink()
                   
                sql='''
                                           select grp_date,
                            case when str_pos is null then null else str_pos end as str_pos,   
                  
                    sum(NUM_SalesAmt) as NUM_SalesAmt, 
                    sum(NUM_cash) as NUM_cash, 
                    sum(    NUM_ccard) as NUM_ccard,
                    sum(    NUM_voucher) as NUM_voucher,
                    sum(    NUM_sodexo) as NUM_sodexo,
                     sum(NUM_gift) as NUM_gift,
                    sum(    NUM_lrvvoc) as NUM_lrvvoc,
                        sum(NUM_Phonepe) as NUM_Phonepe,
                        sum(NUM_GooglePay) as NUM_GooglePay,
                    sum(NUM_loycoupon) as NUM_loycoupon, 
                        sum(NUM_ParkingTKN) as NUM_ParkingTKN,
                        sum(NUM_giftpass) as NUM_giftpass,
                        sum(NUM_paytm) as NUM_paytm,
                    sum(NUM_OtherCpn) as NUM_OtherCpn,
                        sum(NUM_ticket) as NUM_ticket,
                        sum(NUM_TXpress) as NUM_TXpress,
                        sum(NUM_UPIPayment) as NUM_UPIPayment,
                     sum(NUM_RazorPay) as NUM_RazorPay, 
                        sum(NUM_cashDisc) as NUM_cashDisc,
                        sum(NUM_cr_sal) as NUM_cr_sal,
                     sum(NUM_cr_disc) as NUM_cr_disc,
                        sum(NUM_cashinhand) as NUM_cashinhand,
                    sum(NUM_ex_sh) as NUM_ex_sh ,
                        sum(INT_bills) as INT_bills from  (SELECT  p.datetrx::date as grp_date, pos.name as str_pos, 
                  round((sum(COALESCE(p.crsale,0))+sum(COALESCE(p.crdisc,0))+sum(COALESCE(p.payamt,0))),2) AS NUM_SalesAmt, 
                  sum(round(p.um_cash,2)) AS NUM_cash, sum(round(p.um_creditcard,2)) AS NUM_ccard, 
                 sum(round(p.um_voucher,2)) AS NUM_voucher,
                 sum(round(p.sodx,2)) AS NUM_sodexo,
                 sum(round(p.pgiftcard,2)) as NUM_gift,
                 sum(round(p.lrvvoc,2)) as NUM_lrvvoc,
                 sum(round(p.phonepe,2)) as NUM_Phonepe,
                 sum(round(p.googlepay,2)) as NUM_GooglePay,
                 sum(round(p.loycoupon,2)) as NUM_loycoupon,
                 sum(round(p.ParkingTKN,2)) as NUM_ParkingTKN,
                 sum(round(p.giftpass,2)) as NUM_giftpass,
                 sum(round(p.paytm,2)) as NUM_paytm,
                 sum(round(p.othercpn,2)) as NUM_OtherCpn,
                 sum(round(p.ticket,2)) as NUM_ticket,
                 sum(round(p.txpress,2)) as NUM_TXpress,
                 sum(round(p.upipayment,2)) as NUM_UPIPayment,
                 sum(round(p.razorpay,2)) as NUM_RazorPay,
                 sum(round(p.cashdisc,2)) as NUM_cashDisc,
                 sum(round(p.crsale,2)) as NUM_cr_sal,
                 sum(round(COALESCE(p.crdisc , 0::numeric,2))) as NUM_cr_disc,
                 round(COALESCE(s.um_cashtotal, 0::numeric),2) AS NUM_cashinhand, 
                 COALESCE(s.um_cashtotal, 0::numeric,2) - sum(round(p.um_cash,2)) AS NUM_ex_sh, 
                 count(p.billcnt) AS INT_bills
                 FROM ( 
                 with payline as 
                (select c_payment_id,
                sum(case when um_paymodename::text = 'Sodexo'::text  then payamt end) as sodx,
                sum(case when um_paymodename::text = 'PGift Card'::text  then payamt end) as pgiftcard,
                sum(case when um_paymodename::text = 'Ticket'::text  then payamt end) as ticket,
                sum(case when um_paymodename::text = 'LRV Voucher'::text  then payamt end ) as lrvvoc,
                sum(case when um_paymodename::text = 'PhonePe'::text  then payamt end ) as phonepe,
                sum(case when um_paymodename::text = 'GooglePay'::text  then payamt end) as googlepay,
                sum(case when um_paymodename::text = 'Loy Coupon'::text  then payamt end) as loycoupon,
                sum(case when um_paymodename::text = 'Parking TKN'::text  then payamt end) as ParkingTKN,
                sum(case when um_paymodename::text = 'Gift Pass'::text  then payamt end) as giftpass,
                sum(case when um_paymodename::text = 'PayTM'::text  then payamt end) as paytm,
                sum(case when um_paymodename::text = 'Other Cpn'::text  then payamt end) as othercpn,
                sum(case when um_paymodename::text = 'TXPress'::text  then payamt end) as txpress,
                sum(case when um_paymodename::text = 'UPIPayment'::text  then payamt end) as upipayment,
                sum(case when um_paymodename::text = 'RazorPay'::text  then payamt end) as razorpay,
                sum(case when um_paymode_id=100  then pl.payamt end )as cashDisc from 
                um_paymentline pl group by c_payment_id)
                SELECT i.ad_client_id, i.ad_org_id, trunc(i.dateinvoiced::timestamp with time zone) AS datetrx, COALESCE(i.c_pos_id, ( SELECT c_pos.c_pos_id
                           FROM c_pos
                          WHERE c_pos.name::text = i.terminal::text)) AS c_pos_id, 
                p.payamt,
                CASE WHEN (cd.docsubtypeso='WI') then (i.grandtotal - COALESCE(i.um_round_off,0) -coalesce(pll.payamt,0::numeric)) ELSE 0::numeric  END as crsale,
                p.um_cash, p.um_coupon AS um_voucher, p.um_creditcard, i.documentno, 
                1::numeric AS billcnt, round(p.writeoffamt, 2) AS writeoffamt, 
                pl.sodx,
                pl.pgiftcard,
                pl.ticket,
                pl.lrvvoc,
                pl.phonepe,
                pl.googlepay,
                pl.loycoupon,
                pl.ParkingTKN,
                pl.giftpass,
                pl.paytm,
                pl.othercpn,
                pl.txpress,
                pl.upipayment,
                pl.razorpay,
                pl.cashDisc,
                CASE WHEN (cd.docsubtypeso='WI') then coalesce(pll.payamt,0::numeric) ELSE 0::numeric  END as crdisc
                FROM c_invoice i
                LEFT JOIN c_payment p ON (i.c_invoice_id = p.c_invoice_id AND p.c_doctype_id=1000051)
                LEFT JOIN c_payment cp ON (i.c_invoice_id = cp.c_invoice_id AND cp.c_doctype_id<>1000051 and cp.c_payment_id=(select min(c_payment_id) from c_payment cpp where cpp.c_invoice_id=i.c_invoice_id))
                LEFT JOIN um_paymentline pll ON (pll.c_payment_id = cp.c_payment_id)
                LEFT JOIN payline pl ON pl.c_payment_id = p.c_payment_id
                LEFT JOIN c_order o ON o.c_order_id = i.c_order_id
                left join c_doctype cd on cd.c_doctype_id=o.c_doctype_id 
                WHERE i.dateinvoiced::date >= '%s' and  i.dateinvoiced::date <='%s'  
                AND i.issotrx = 'Y'::bpchar AND (i.c_pos_id > 0::numeric OR i.terminal IS NOT NULL) AND (i.docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar]))
                GROUP BY i.ad_client_id, i.ad_org_id, i.dateinvoiced, i.c_pos_id, p.payamt,pll.payamt, p.um_cash, p.um_coupon, p.um_creditcard, i.documentno, i.grandtotal,i.um_round_off, 
                p.writeoffamt, i.terminal, p.c_payment_id,i.c_doctype_id,pl.sodx,pl.pgiftcard,pl.ticket,pl.lrvvoc,pl.phonepe,pl.googlepay,pl.loycoupon,pl.ParkingTKN,pl.giftpass,pl.paytm,pl.othercpn,pl.txpress,pl.upipayment,pl.razorpay,pl.cashDisc,
                docsubtypeso
                ORDER BY i.dateinvoiced DESC
                ) p
                   inner join c_pos pos on (pos.c_pos_id = p.c_pos_id)
                   LEFT JOIN um_settlement s ON s.c_pos_id = p.c_pos_id AND s.um_settlementdate = p.datetrx
                GROUP BY p.ad_client_id, p.ad_org_id, pos.c_pos_id,pos.name, p.datetrx, s.um_cashtotal 
                union all
                        SELECT  p.datetrx::date as grp_date, null as str_pos, 
                  round((sum(COALESCE(p.crsale,0))+sum(COALESCE(p.crdisc,0))+sum(COALESCE(p.payamt,0))),2) AS NUM_SalesAmt, 
                  sum(round(p.um_cash,2)) AS NUM_cash, sum(round(p.um_creditcard,2)) AS NUM_ccard, 
                 sum(round(p.um_voucher,2)) AS NUM_voucher,
                 sum(round(p.sodx,2)) AS NUM_sodexo,
                 sum(round(p.pgiftcard,2)) as NUM_gift,
                 sum(round(p.lrvvoc,2)) as NUM_lrvvoc,
                 sum(round(p.phonepe,2)) as NUM_Phonepe,
                 sum(round(p.googlepay,2)) as NUM_GooglePay,
                 sum(round(p.loycoupon,2)) as NUM_loycoupon,
                 sum(round(p.ParkingTKN,2)) as NUM_ParkingTKN,
                 sum(round(p.giftpass,2)) as NUM_giftpass,
                 sum(round(p.paytm,2)) as NUM_paytm,
                 sum(round(p.othercpn,2)) as NUM_OtherCpn,
                 sum(round(p.ticket,2)) as NUM_ticket,
                 sum(round(p.txpress,2)) as NUM_TXpress,
                 sum(round(p.upipayment,2)) as NUM_UPIPayment,
                 sum(round(p.razorpay,2)) as NUM_RazorPay,
                 sum(round(p.cashdisc,2)) as NUM_cashDisc,
                 sum(round(p.crsale,2)) as NUM_cr_sal,
                 sum(round(COALESCE(p.crdisc , 0::numeric,2))) as NUM_cr_disc,
                 round(COALESCE(s.um_cashtotal, 0::numeric),2) AS NUM_cashinhand, 
                 COALESCE(s.um_cashtotal, 0::numeric,2) - sum(round(p.um_cash,2)) AS NUM_ex_sh, 
                 count(p.billcnt) AS INT_bills
                 FROM ( 
                 with payline as 
                (select c_payment_id,
                sum(case when um_paymodename::text = 'Sodexo'::text  then payamt end) as sodx,
                sum(case when um_paymodename::text = 'PGift Card'::text  then payamt end) as pgiftcard,
                sum(case when um_paymodename::text = 'Ticket'::text  then payamt end) as ticket,
                sum(case when um_paymodename::text = 'LRV Voucher'::text  then payamt end ) as lrvvoc,
                sum(case when um_paymodename::text = 'PhonePe'::text  then payamt end ) as phonepe,
                sum(case when um_paymodename::text = 'GooglePay'::text  then payamt end) as googlepay,
                sum(case when um_paymodename::text = 'Loy Coupon'::text  then payamt end) as loycoupon,
                sum(case when um_paymodename::text = 'Parking TKN'::text  then payamt end) as ParkingTKN,
                sum(case when um_paymodename::text = 'Gift Pass'::text  then payamt end) as giftpass,
                sum(case when um_paymodename::text = 'PayTM'::text  then payamt end) as paytm,
                sum(case when um_paymodename::text = 'Other Cpn'::text  then payamt end) as othercpn,
                sum(case when um_paymodename::text = 'TXPress'::text  then payamt end) as txpress,
                sum(case when um_paymodename::text = 'UPIPayment'::text  then payamt end) as upipayment,
                sum(case when um_paymodename::text = 'RazorPay'::text  then payamt end) as razorpay,
                sum(case when um_paymode_id=100  then pl.payamt end )as cashDisc from 
                um_paymentline pl group by c_payment_id)
                SELECT i.ad_client_id, i.ad_org_id, trunc(i.dateinvoiced::timestamp with time zone) AS datetrx, COALESCE(i.c_pos_id, ( SELECT c_pos.c_pos_id
                           FROM c_pos
                          WHERE c_pos.name::text = i.terminal::text)) AS c_pos_id, 
                p.payamt,
                CASE WHEN (cd.docsubtypeso='WI') then (i.grandtotal - COALESCE(i.um_round_off,0) -coalesce(pll.payamt,0::numeric)) ELSE 0::numeric  END as crsale,
                p.um_cash, p.um_coupon AS um_voucher, p.um_creditcard, i.documentno, 
                1::numeric AS billcnt, round(p.writeoffamt, 2) AS writeoffamt, 
                pl.sodx,
                pl.pgiftcard,
                pl.ticket,
                pl.lrvvoc,
                pl.phonepe,
                pl.googlepay,
                pl.loycoupon,
                pl.ParkingTKN,
                pl.giftpass,
                pl.paytm,
                pl.othercpn,
                pl.txpress,
                pl.upipayment,
                pl.razorpay,
                pl.cashDisc,
                CASE WHEN (cd.docsubtypeso='WI') then coalesce(pll.payamt,0::numeric) ELSE 0::numeric  END as crdisc
                FROM c_invoice i
                LEFT JOIN c_payment p ON (i.c_invoice_id = p.c_invoice_id AND p.c_doctype_id=1000051)
                LEFT JOIN c_payment cp ON (i.c_invoice_id = cp.c_invoice_id AND cp.c_doctype_id<>1000051 and cp.c_payment_id=(select min(c_payment_id) from c_payment cpp where cpp.c_invoice_id=i.c_invoice_id))
                LEFT JOIN um_paymentline pll ON (pll.c_payment_id = cp.c_payment_id)
                LEFT JOIN payline pl ON pl.c_payment_id = p.c_payment_id
                LEFT JOIN c_order o ON o.c_order_id = i.c_order_id
                left join c_doctype cd on cd.c_doctype_id=o.c_doctype_id 
                WHERE i.dateinvoiced::date >= '%s' and  i.dateinvoiced::date <='%s'  
                AND i.issotrx = 'Y'::bpchar AND (i.c_pos_id > 0::numeric OR i.terminal IS NOT NULL) AND (i.docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar]))
                GROUP BY i.ad_client_id, i.ad_org_id, i.dateinvoiced, i.c_pos_id, p.payamt,pll.payamt, p.um_cash, p.um_coupon, p.um_creditcard, i.documentno, i.grandtotal,i.um_round_off, 
                p.writeoffamt, i.terminal, p.c_payment_id,i.c_doctype_id,pl.sodx,pl.pgiftcard,pl.ticket,pl.lrvvoc,pl.phonepe,pl.googlepay,pl.loycoupon,pl.ParkingTKN,pl.giftpass,pl.paytm,pl.othercpn,pl.txpress,pl.upipayment,pl.razorpay,pl.cashDisc,
                docsubtypeso
                ORDER BY i.dateinvoiced DESC
                ) p
                   inner join c_pos pos on (pos.c_pos_id = p.c_pos_id)
                   LEFT JOIN um_settlement s ON s.c_pos_id = p.c_pos_id AND s.um_settlementdate = p.datetrx
                GROUP BY p.ad_client_id, p.ad_org_id, pos.c_pos_id,pos.name, p.datetrx, s.um_cashtotal)k 
                group by k.grp_date,k.str_pos 
                Order by k.grp_date,k.str_pos 
         '''  %(start_date,end_date,start_date,end_date)
                                  
                cursor.execute(sql)
                sale_data = cursor.fetchall()
                for row in sale_data:                
                        dict = {'date':row[0],'pos':row[1] , 'sale_amount':row[2] ,'cash':row[3] ,
                                'ccard':row[4] ,'voucher':row[5] ,'sodexo':row[6] ,'gift':row[7],
                                'lrvvoc':row[8] ,
                                 'phonepe':row[9],'googlepay':row[10] , 
                                'loycoupon':row[11] ,'parkingtkn':row[12] ,'giftpass':row[13] ,
                                'paytm':row[14],'othercpn':row[15] , 'ticket':row[16],'txpress':row[17] ,
                                'upipayment':row[18] ,
                                'razorpay':row[19] , 'cashdisc':row[20] ,
                                'cr_sal':row[21] ,
                                 'cr_disc':row[22],'cashinhand':row[23] ,'ex_sh':row[24] ,'bills':row[25]}
                        lis.append(dict)
                return lis
            except (Exception, psycopg2.Error) as error:
                raise UserError(_("Error while fetching data from PostgreSQL "))
            finally:
                if db_conn:
                    cursor.close() 
                    db_connect.close()
                   
              
           
        tamt = 0

        summary_sale_line = []
        seq = 0
        sum_amt = 0
        cash_sum_amt = 0
        voucher_sum_amt = 0
        in_hand_sum_amt = 0
        ex_short_amt = 0
        credit_sum_amt = 0
        ccard_sum_amt = 0
        sodexo_sum_amt = 0
        lrvvoc_sum_amt = 0
        phonepe_sum_amt = 0
        gift_sum_amt = 0
        googlepay_sum_amt = 0
        loycoupon_sum_amt = 0
        parkingtkn_sum_amt = 0
        giftpass_sum_amt = 0
        paytm_sum_amt= 0
        othercpn_sum_amt= 0
        ticket_sum_amt= 0
        txpress_sum_amt= 0
        upipayment_sum_amt= 0
        razorpay_sum_amt= 0 
        cashdisc_sum_amt= 0
        cr_sal_sum_amt= 0
        cr_disc_sum_amt= 0
        ex_sh_sum_amt= 0
        bill_sum_amt = 0 
        for line in get_summary_lines(self): 
            if line['sale_amount']:
                sum_amt+=line['sale_amount']
                if line['cash']:
                    cash_sum_amt+=line['cash'] 
                if line['voucher']:
                    voucher_sum_amt+=line['voucher']
                if line['cashinhand']:
                    in_hand_sum_amt+=line['cashinhand'] 
                if line['bills']:
                    bill_sum_amt+=line['bills']
                if line['ccard']:
                    ccard_sum_amt+=line['ccard']
                if line['sodexo']:
                    sodexo_sum_amt+=line['sodexo'] 
                if line['gift']:
                    gift_sum_amt+=line['gift'] 
                if line['lrvvoc']:
                    lrvvoc_sum_amt+=line['lrvvoc'] 
                if line['phonepe']:
                    phonepe_sum_amt+=line['phonepe'] 
                if line['googlepay']:
                    googlepay_sum_amt+=line['googlepay'] 
                if line['loycoupon']:
                    loycoupon_sum_amt+=line['loycoupon'] 
                if line['parkingtkn']:
                    parkingtkn_sum_amt+=line['parkingtkn'] 
                if line['giftpass']:
                    giftpass_sum_amt+=line['giftpass'] 
                if line['paytm']:
                    paytm_sum_amt+=line['paytm'] 
                if line['othercpn']:
                    othercpn_sum_amt+=line['othercpn'] 
                if line['ticket']:
                    ticket_sum_amt+=line['ticket'] 
                if line['txpress']:
                    txpress_sum_amt+=line['txpress'] 
                if line['upipayment']:
                    upipayment_sum_amt+=line['upipayment'] 
                if line['razorpay']:
                    razorpay_sum_amt+=line['razorpay']  
                if line['cashdisc']:
                    cashdisc_sum_amt+=line['cashdisc'] 
                if line['cr_sal']:
                    cr_sal_sum_amt+=line['cr_sal'] 
                if line['cr_disc']:
                    cr_disc_sum_amt+=line['cr_disc'] 
                if line['ex_sh']:
                    ex_sh_sum_amt+=line['ex_sh'] 
                    
                summary_sale_line.append((0,0,{
                                    'date' : line['date'],
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
          
                                   
                                         }))
        if  summary_sale_line:
            summary_sale_line.append((0,0,{
                'sale_amount' : sum_amt,
                'cash': cash_sum_amt, 
                'voucher':voucher_sum_amt,
                'cashinhand':in_hand_sum_amt,  
                'bills':bill_sum_amt,
                'ccard': ccard_sum_amt, 
                'sodexo':sodexo_sum_amt,
                'lrvvoc':lrvvoc_sum_amt ,
                 'phonepe' : phonepe_sum_amt ,
                 'gift': gift_sum_amt,
                'googlepay' :googlepay_sum_amt, 
                 'loycoupon':loycoupon_sum_amt ,
                 'parkingtkn' :parkingtkn_sum_amt,
                  'giftpass' :giftpass_sum_amt ,
                   'paytm':paytm_sum_amt,
                   'othercpn':othercpn_sum_amt,
                    'ticket' :ticket_sum_amt,
                    'txpress' :txpress_sum_amt,
                    'upipayment' :upipayment_sum_amt,
                    'razorpay' :razorpay_sum_amt,
                   'cashdisc' : cashdisc_sum_amt,
                     'cr_sal' : cr_sal_sum_amt,
                     'cr_disc' :cr_disc_sum_amt,
                      'ex_sh' :ex_sh_sum_amt,
                }))
          
        vals = { 
                'start_date':self.start_date,             
                'end_date': self.end_date,
                'company_id' : self.company_id.name,
                'summary_sale_line': summary_sale_line, 
                }
        sales_wise_reports_id = self.env['summary.sales.report.screen.wzd.ss'].create(vals)

        res = self.env['ir.model.data'].check_object_reference(
                                            'ss_pos_reports', 'view_summary_wzd_report')
        return {
                    'name': 'Summary Sales Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'summary.sales.report.screen.wzd.ss',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': sales_wise_reports_id.id,
            }
       
       
class summary_sales_screen_wzd(models.Model):
    _name = "summary.sales.report.screen.wzd.ss"
    _description = "Summary Sales Reports"
    
    name = fields.Char(string="Name", default='Summary of Sales Report')
    start_date = fields.Date(string="Date From")
    end_date = fields.Date(string="Date To")
    company_id = fields.Char("Company")
    summary_sale_line = fields.One2many('summary.sales.report.screen.line.ss','summary_order_id',string='Open Order Line')
    
    def print_summary_excel_report(self):
        filename= 'Summary of Sales Report.xls'
        workbook= xlwt.Workbook(encoding="UTF-8")
        style_header = xlwt.easyxf('font: bold on; font:height 230; align: wrap No; borders: left thin, right thin, top thin, bottom thin;')
        style = xlwt.easyxf('font:height 230; align: wrap No;borders: left thin, right thin, top thin, bottom thin;')
        header=xlwt.easyxf('pattern: pattern solid, fore_colour light_orange;''font:height 400; align: horiz center;font:bold True;' "borders: top thin,bottom thin , left thin, right thin")
        style = xlwt.easyxf('font:height 230; align: wrap No;')
        base_style = xlwt.easyxf('align: wrap yes')
        date_style = xlwt.easyxf('align: wrap yes', num_format_str='DD-MM-YYYY')
        datetime_style = xlwt.easyxf('align: wrap yes', num_format_str='DD-MM-YYYY HH:mm:SS')
        sheet= workbook.add_sheet('Summary of Sales Report')
        format6 = xlwt.easyxf('pattern: pattern solid, fore_colour light_yellow;''font:height 280,bold True;align: horiz left;'"borders: top thin,bottom thin , left thin, right thin")
        format7 = xlwt.easyxf('pattern: pattern solid, fore_colour light_yellow;''font:height 280,bold True;align: horiz center;'"borders: top thin,bottom thin , left thin, right thin")
        format1 = xlwt.easyxf('font: bold off, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color white;')
        my_format = xlwt.easyxf(num_format_str= '0.00')
        
        start_date = self.start_date or ''
        end_date = self.end_date  or ''
        company_id = self.company_id  or ''
        

        sheet.col(0).width = 850*5
        sheet.col(1).width = 850*5
        sheet.col(2).width = 850*7
        sheet.col(3).width = 850*7
        sheet.col(4).width = 850*6
        sheet.col(5).width = 850*6
        sheet.col(6).width = 850*7
        sheet.col(7).width = 850*5
        sheet.col(8).width = 850*5
        sheet.col(9).width = 850*5
        sheet.col(10).width = 850*5
        sheet.col(11).width = 850*5
        sheet.col(12).width = 850*5
        sheet.col(13).width = 850*5
        sheet.col(14).width = 850*6
        sheet.col(15).width = 850*6
        sheet.col(16).width = 850*6
        sheet.col(17).width = 850*6
        sheet.col(18).width = 850*6
        sheet.col(19).width = 850*5
        sheet.col(20).width = 850*5
        sheet.col(21).width = 850*5
        sheet.col(22).width = 850*5
        sheet.col(23).width = 850*5
        sheet.col(24).width = 850*5
        sheet.col(25).width = 850*5
        sheet.col(26).width = 850*5
        sheet.col(27).width = 850*5
        sheet.row(0).height = 70*5
        sheet.row(1).height = 70*5
        sheet.row(2).height = 70*5
        sheet.row(3).height = 70*5
        sheet.row(4).height = 70*5
        sheet.row(5).height = 70*5
        sheet.row(6).height = 70*5
        sheet.row(7).height = 70*5
        sheet.row(8).height = 70*5
        sheet.row(9).height = 70*5
        sheet.row(10).height = 70*5
        sheet.row(11).height = 70*5
        sheet.row(12).height = 70*5
        sheet.row(13).height = 70*5
        sheet.row(14).height = 70*5
        sheet.row(15).height = 70*5
        sheet.row(16).height = 70*5
        sheet.row(17).height = 70*5
        sheet.row(18).height = 70*5
        sheet.row(19).height = 70*5
        sheet.row(20).height = 70*5
        sheet.row(21).height = 70*5
        sheet.row(22).height = 70*5
        sheet.row(23).height = 70*5 
        sheet.row(24).height = 70*5
        sheet.row(25).height = 70*5
        sheet.row(26).height = 70*5
        sheet.write(2, 0, 'Date', format7)
        sheet.write(2, 1, 'POS', format7)
        sheet.write(2, 2, 'Sales Amount', format7)
        sheet.write(2, 3, 'Cash', format7)
        sheet.write(2, 4, 'ccard', format7)
        sheet.write(2, 5, 'Voucher', format7)
        sheet.write(2, 6, 'sodexo', format7)
        sheet.write(2, 7,'gift',format7)
        sheet.write(2, 8, 'Irvvoc', format7)
        sheet.write(2, 9, 'Phonepe', format7)
        sheet.write(2, 10, 'Google Pay', format7)
        sheet.write(2, 11, 'loycoupon', format7)
        sheet.write(2, 12, 'parkingtkn', format7)
        sheet.write(2, 13, 'Giftpass', format7)
        sheet.write(2, 14, 'Paytm', format7)
        sheet.write(2, 15, 'othercpn', format7)
        sheet.write(2, 16, 'Ticket', format7)
        sheet.write(2, 17, 'txpress', format7)
        sheet.write(2, 18,'upipayment',format7)
        sheet.write(2, 19, 'razorpay', format7)
        sheet.write(2, 20, 'cashdisc', format7)
        sheet.write(2, 21, 'cr_sal', format7)
        sheet.write(2, 22, 'cr_disc', format7)
        sheet.write(2, 23, 'cashinhand', format7)
        sheet.write(2, 24, 'ex_sh', format7)
        sheet.write(2, 25, 'bills', format7)
        sheet.write_merge(0, 1, 0, 8, 'Summary of Sales Report',header) 
   
           
               
        sql = '''    
                select to_char(date,'dd/mm/yyyy'),pos,sale_amount,cash,
                    ccard,voucher,sodexo,gift,lrvvoc,
                     phonepe,googlepay,loycoupon,parkingtkn,
                     giftpass,paytm,othercpn,ticket,txpress,
                     upipayment,razorpay,cashdisc,
                     cr_sal,cr_disc,cashinhand ,ex_sh,bills from summary_sales_report_screen_line_ss 
                     where summary_order_id=(select max(summary_order_id) from summary_sales_report_screen_line_ss)
                     '''
           

           
        self.env.cr.execute(sql)
        rows2 = self.env.cr.fetchall()
        for row_index, row in enumerate(rows2):
            for cell_index, cell_value in enumerate(row):
                cell_style = format1 
                if isinstance(cell_value, str):
                    cell_value = re.sub("\r", " ", cell_value)
                elif isinstance(cell_value,float) :
                    cell_style =  format1 
                    sheet.row(row_index+1).height = 70*5    
                sheet.write(row_index + 3, cell_index, cell_value,format1)    
        fp =io.BytesIO()
      
        workbook.save(fp)
        export_id = self.env['excel.extended.summary.sales.rep.ss'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        
        fp.seek(0)
        data = fp.read()
        fp.close()

        return{
              'view_mode': 'form',
              'res_id': export_id.id,
              'res_model': 'excel.extended.summary.sales.rep.ss',
              'type': 'ir.actions.act_window',
              'context': False, 
          
            }
        
summary_sales_screen_wzd()
 
class summary_sales_screen_line(models.Model):
    _name = "summary.sales.report.screen.line.ss"
    _description = "Open Orders summary Line"
    
    summary_order_id = fields.Many2one('summary.sales.report.screen.wzd.ss',string='summary_order_id',ondelete='cascade')
    date = fields.Date('Date')
    pos = fields.Char('POS')
    sale_amount = fields.Float('Sales Amount')
    cash = fields.Float('Cash')
    ccard = fields.Float('ccard')
    voucher = fields.Float('Voucher')
    sodexo = fields.Float('sodexo')
    gift = fields.Float('gift')
    lrvvoc = fields.Float('Irvvoc')
    phonepe = fields.Float('Phonepe')
    googlepay = fields.Float('Google Pay')
    loycoupon = fields.Float('loycoupon')
    parkingtkn = fields.Float('parkingtkn')
    giftpass = fields.Float('Giftpass')
    paytm = fields.Float('Paytm')
    othercpn = fields.Float('othercpn')
    ticket = fields.Float('Ticket')
    txpress = fields.Float('txpress')
    upipayment = fields.Float('upipayment')
    razorpay = fields.Float('razorpay')
    cashdisc = fields.Float('cashdisc')
    cr_sal = fields.Float('cr_sal')
    cr_disc = fields.Float('cr_disc')
    cashinhand = fields.Float('cashinhand')
    ex_sh = fields.Float('ex_sh')
    bills = fields.Float('bills')
           
summary_sales_screen_line()

     
class excel_extended_summary_saless_rep(models.Model):
    _name= "excel.extended.summary.sales.rep.ss"

    name = fields.Char(string="Name", default='Download Excel Report')    
    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64) 
    
    
