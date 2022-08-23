from datetime import datetime
from datetime import date 
from dateutil.relativedelta import relativedelta
from odoo.osv import osv
from odoo import api, fields, models
from odoo import exceptions, _
from odoo.exceptions import UserError
import xlwt
import io
import base64
import re
import xlsxwriter
from itertools import count
from email.policy import default
import psycopg2


DATE_FORMAT_1 = "%d-%m-%y"
DATE_FORMAT_2 = "%d/%m/%y"
DATE_FORMAT_3 = "%d/%m/%y"

class teriminal_wise_sales_details_wzd(models.Model):
    _name = "sales.summary.report"
       
    start_date = fields.Date('Date From') 
    end_date = fields.Date('Date To')
    company_id = fields.Many2one('res.company',string='Company',default=lambda self:self.env.company.id)
        
    def print_sales_report(self):

        def get_lines(self):
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
                self.env['sales.summary.screen.line'].search([]).unlink()
            
                sql=''' 
                  select grp_date, pos,  cashier,
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
                        sum(NUM_AdvPaid) as NUM_AdvPaid,
                        sum(NUM_cashDisc) as NUM_cashDisc,
                        sum(NUM_cr_sal) as NUM_cr_sal,
                     sum(NUM_cr_disc) as NUM_cr_disc,
                        sum(NUM_cashinhand) as NUM_cashinhand,
                    sum(NUM_ex_sh) as NUM_ex_sh ,
                        sum(INT_bills) as INT_bills from(SELECT  p.datetrx as grp_date, null as pos, null as cashier,
                    ROUND((sum(COALESCE(p.crsale,0))+sum(COALESCE(p.crdisc,0))+sum(COALESCE(p.payamt,0)-COALESCE(p.um_exchangeamt,0))),2) AS NUM_SalesAmt, 
                     ROUND(sum(p.um_cash),2) AS NUM_cash, 
                    ROUND( sum(p.um_creditcard),2) AS NUM_ccard,
                    ROUND(sum(p.um_voucher),2) AS NUM_voucher,
                    ROUND(sum(p.sodx),2) AS NUM_sodexo,
                     ROUND(sum(p.pgiftcard),2) as NUM_gift,
                    ROUND(sum(p.lrvvoc),2) as NUM_lrvvoc,
                    ROUND(sum(p.phonepe),2) as NUM_Phonepe,
                    ROUND(sum(p.googlepay),2) as NUM_GooglePay,
                    ROUND( sum(p.loycoupon),2) as NUM_loycoupon,
                    ROUND(sum(p.ParkingTKN),2) as NUM_ParkingTKN,
                    ROUND(sum(p.giftpass),2) as NUM_giftpass,
                    ROUND(sum(p.paytm),2) as NUM_paytm,
                    ROUND( sum(p.othercpn),2) as NUM_OtherCpn,
                    ROUND(sum(p.ticket),2) as NUM_ticket,
                    ROUND(sum(p.txpress),2) as NUM_TXpress,
                    ROUND(sum(p.upipayment),2) as NUM_UPIPayment,
                    ROUND( sum(p.razorpay),2) as NUM_RazorPay,
                    ROUND(sum(COALESCE(p.advpaid, 0::numeric)),2) as NUM_AdvPaid,
                    ROUND(sum(p.cashdisc),2) as NUM_cashDisc,
                    ROUND( sum(p.crsale),2) as NUM_cr_sal,
                    ROUND( sum(COALESCE(p.crdisc , 0::numeric)),2) as NUM_cr_disc,
                    ROUND(COALESCE(s.um_cashtotal, 0::numeric),2) AS NUM_cashinhand,
                    ROUND(COALESCE(s.um_cashtotal, 0::numeric) - sum(p.um_cash),2) AS NUM_ex_sh,
                    count(p.billcnt) AS INT_bills FROM ( 
                    select a.ad_client_id, a.ad_org_id, a.datetrx, a.c_pos_id,a.ad_user_id,a.billcnt,a.documentno,
                    case when a.pay_rank=1 then a.payamt  else 0 end as payamt,case when a.pay_rank=1 then a.um_cash  else 0 end as um_cash,
                    case when a.pay_rank=1 then a.um_creditcard  else 0 end as um_creditcard,case when a.pay_rank=1 then a.crsale  else 0 end as crsale,
                    case when a.pay_rank=1 then a.writeoffamt  else 0 end as writeoffamt,case when a.pay_rank=1 then a.sodx  else 0 end as sodx,
                    case when a.pay_rank=1 then a.um_voucher  else 0 end as um_voucher,case when a.pay_rank=1 then a.pgiftcard  else 0 end as pgiftcard,
                    case when a.pay_rank=1 then a.ticket  else 0 end as ticket,case when a.pay_rank=1 then a.lrvvoc  else 0 end as lrvvoc,
                    case when a.pay_rank=1 then a.phonepe  else 0 end as phonepe,case when a.pay_rank=1 then a.googlepay  else 0 end as googlepay,
                    case when a.pay_rank=1 then a.loycoupon  else 0 end as loycoupon,case when a.pay_rank=1 then a.ParkingTKN  else 0 end as ParkingTKN,
                    case when a.pay_rank=1 then a.upipayment  else 0 end as upipayment,case when a.pay_rank=1 then a.giftpass  else 0 end as giftpass,
                    case when a.pay_rank=1 then a.paytm  else 0 end as paytm,case when a.pay_rank=1 then a.othercpn  else 0 end as othercpn,
                    case when a.pay_rank=1 then a.txpress  else 0 end as txpress,case when a.pay_rank=1 then a.razorpay  else 0 end as razorpay,
                    case when a.pay_rank=1 then a.advpaid  else 0 end as advpaid,case when a.pay_rank=1 then a.cashDisc  else 0 end as cashDisc,
                    case when a.pay_rank=1 then a.um_exchangeamt  else 0 end as um_exchangeamt,
                    case when a.pay_rank=1 then a.crdisc  else 0 end as crdisc from (
                    with payline as (select c_payment_id,sum(case when um_paymodename::text = 'Sodexo'::text  then payamt end) as sodx,
                    sum(case when um_paymodename::text = 'PGift Card'::text  then payamt end) as pgiftcard,
                    sum(case when um_paymodename::text = 'Ticket'::text  then payamt end) as ticket,
                    sum(case when um_paymodename::text = 'LS-LRV Voucher'::text  then payamt end ) as lrvvoc,
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
                    sum(case when um_paymodename::text = 'AdvPaid'::text  then payamt end) as advpaid,
                    sum(case when um_paymode_id=100  then pl.payamt end )as cashDisc from um_paymentline pl group by c_payment_id)
                    SELECT i.ad_client_id, i.ad_org_id, trunc(i.dateinvoiced::timestamp with time zone) AS datetrx,
                    COALESCE(i.c_pos_id, ( SELECT c_pos.c_pos_id FROM c_pos WHERE c_pos.name::text = i.terminal::text)) AS c_pos_id,i.um_cashier_id as ad_user_id,
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then p1.payamt else p.payamt END as payamt,1::numeric AS billcnt,i.documentno,
                    CASE 
                    WHEN (cd.docsubtypeso='WI' and COALESCE(pa.c_paymentallocate_id,0)>0) 
                    then (i.grandtotal - COALESCE(i.um_round_off,0) -coalesce(pll1.payamt,0::numeric)) 
                    WHEN (cd.docsubtypeso='WI' and COALESCE(pa.c_paymentallocate_id,0)=0) 
                    then (i.grandtotal - COALESCE(i.um_round_off,0) -coalesce(pll.payamt,0::numeric)) 
                    ELSE 0::numeric  
                    END as crsale,
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then p1.um_cash else p.um_cash END as um_cash, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then p1.um_coupon else p.um_coupon END as um_voucher, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then p1.um_creditcard else p.um_creditcard END as um_creditcard, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then round(p1.writeoffamt, 2) else round(p.writeoffamt, 2) END as writeoffamt, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.sodx else pl.sodx END as sodx, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.pgiftcard else pl.pgiftcard END as pgiftcard, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.ticket else pl.ticket END as ticket, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.lrvvoc else pl.lrvvoc END as lrvvoc, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.phonepe else pl.phonepe END as phonepe,
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.googlepay else pl.googlepay END as googlepay, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.loycoupon else pl.loycoupon END as loycoupon, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.ParkingTKN else pl.ParkingTKN END as ParkingTKN, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.giftpass else pl.giftpass END as giftpass, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.paytm else pl.paytm END as paytm, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.othercpn else pl.othercpn END as othercpn, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.txpress else pl.txpress END as txpress, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.upipayment else pl.upipayment END as upipayment, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.razorpay else pl.razorpay END as razorpay, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.advpaid else pl.advpaid END as advpaid, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.cashDisc else pl.cashDisc END as cashDisc, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then p1.um_exchangeamt else p.um_exchangeamt END as um_exchangeamt,
                    case 
                    when (cd.docsubtypeso='WI' and COALESCE(pa.c_paymentallocate_id,0)>0) then coalesce(pll1.payamt,0::numeric)  
                    when (cd.docsubtypeso='WI' and COALESCE(pa.c_paymentallocate_id,0)=0) then coalesce(pll.payamt,0::numeric) ELSE 0::numeric 
                    END as crdisc,
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then rank()over(partition by p1.c_payment_id order by i.c_invoice_id) 
                    when (COALESCE(pa.c_paymentallocate_id,0)=0 and p.c_payment_id>0) then  rank()over(partition by p.c_payment_id order by i.c_invoice_id)
                    else 1 end as pay_rank FROM c_invoice i
                    LEFT JOIN c_paymentallocate pa ON (i.c_invoice_id = pa.c_invoice_id)
                    LEFT JOIN c_payment p1 ON (pa.c_payment_id = p1.c_payment_id AND p1.c_doctype_id=1000051)
                    LEFT JOIN c_payment cp1 ON (pa.c_payment_id = cp1.c_payment_id AND cp1.c_doctype_id<>1000051 
                    and cp1.c_payment_id=(select min(c_payment_id) from c_payment cpp1 where cpp1.c_invoice_id=i.c_invoice_id))
                    LEFT JOIN c_payment p ON (i.c_invoice_id = p.c_invoice_id AND p.c_doctype_id=1000051)
                    LEFT JOIN c_payment cp ON (i.c_invoice_id = cp.c_invoice_id AND cp.c_doctype_id<>1000051 
                    and cp.c_payment_id=(select min(c_payment_id) from c_payment cpp where cpp.c_invoice_id=i.c_invoice_id))
                    LEFT JOIN um_paymentline pll ON (pll.c_payment_id = cp.c_payment_id)
                    LEFT JOIN payline pl ON pl.c_payment_id = p.c_payment_id
                    LEFT JOIN um_paymentline pll1 ON (pll1.c_payment_id = cp1.c_payment_id)
                    LEFT JOIN payline pl1 ON pl1.c_payment_id = p1.c_payment_id
                    LEFT JOIN c_order o ON o.c_order_id = i.c_order_id
                    left join c_doctype cd on cd.c_doctype_id=o.c_doctype_id
                    WHERE i.dateinvoiced::date >= '%s' and  i.dateinvoiced::date <='%s' AND i.issotrx = 'Y'::bpchar AND (i.c_pos_id > 0::numeric OR i.terminal IS NOT NULL) AND (i.docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar]))
                    GROUP BY i.ad_client_id, i.ad_org_id,i.um_cashier_id, i.dateinvoiced, i.c_pos_id, p.payamt,pll.payamt, p.um_cash, p.um_coupon, p.um_creditcard, i.documentno, i.grandtotal,i.um_round_off,p.writeoffamt,i.terminal,p.c_payment_id,i.c_doctype_id,pl.sodx,pl.pgiftcard,pl.ticket,pl.lrvvoc,pl.phonepe,pl.googlepay,
                    pl.loycoupon,pl.ParkingTKN,pl.giftpass,pl.paytm,pl.othercpn,pl.txpress,pl.upipayment,pl.razorpay,pl.cashDisc,docsubtypeso,p.um_exchangeamt,pl.advpaid,
                    p.c_invoice_id,p1.um_cash,p1.um_coupon,p1.um_creditcard,p1.writeoffamt,pl1.sodx,pl1.pgiftcard,pl1.ticket,pl1.lrvvoc,pl1.phonepe,pl1.googlepay,pl1.loycoupon,
                    pl1.ParkingTKN,pl1.giftpass,pl1.paytm,pl1.othercpn,pl1.txpress,pl1.upipayment,pl1.razorpay,pl1.advpaid,pl1.cashDisc,p1.um_exchangeamt,pl1.advpaid,
                    pa.c_paymentallocate_id,pll1.payamt,i.c_invoice_id,p1.c_payment_id,p1.payamt ORDER BY i.dateinvoiced DESC)a ) p
                    inner join c_pos pos on (pos.c_pos_id = p.c_pos_id)
                    inner join ad_user u on (u.ad_user_id=p.ad_user_id)
                    LEFT JOIN um_settlement s ON s.c_pos_id = p.c_pos_id AND s.um_settlementdate = p.datetrx and s.salesrep_id=p.ad_user_id
                    GROUP BY p.ad_client_id, p.ad_org_id, pos.c_pos_id,pos.name, p.datetrx, s.um_cashtotal ,u.name
                    union all
                    (  SELECT  p.datetrx as grp_date, pos.name as pos, u.name as cashier,
                    ROUND((sum(COALESCE(p.crsale,0))+sum(COALESCE(p.crdisc,0))+sum(COALESCE(p.payamt,0)-COALESCE(p.um_exchangeamt,0))),2) AS NUM_SalesAmt, 
                     ROUND(sum(p.um_cash),2) AS NUM_cash, 
                    ROUND( sum(p.um_creditcard),2) AS NUM_ccard,
                    ROUND(sum(p.um_voucher),2) AS NUM_voucher,
                    ROUND(sum(p.sodx),2) AS NUM_sodexo,
                     ROUND(sum(p.pgiftcard),2) as NUM_gift,
                    ROUND(sum(p.lrvvoc),2) as NUM_lrvvoc,
                    ROUND(sum(p.phonepe),2) as NUM_Phonepe,
                    ROUND(sum(p.googlepay),2) as NUM_GooglePay,
                    ROUND( sum(p.loycoupon),2) as NUM_loycoupon,
                    ROUND(sum(p.ParkingTKN),2) as NUM_ParkingTKN,
                    ROUND(sum(p.giftpass),2) as NUM_giftpass,
                    ROUND(sum(p.paytm),2) as NUM_paytm,
                    ROUND( sum(p.othercpn),2) as NUM_OtherCpn,
                    ROUND(sum(p.ticket),2) as NUM_ticket,
                    ROUND(sum(p.txpress),2) as NUM_TXpress,
                    ROUND(sum(p.upipayment),2) as NUM_UPIPayment,
                    ROUND( sum(p.razorpay),2) as NUM_RazorPay,
                    ROUND(sum(COALESCE(p.advpaid, 0::numeric)),2) as NUM_AdvPaid,
                    ROUND(sum(p.cashdisc),2) as NUM_cashDisc,
                    ROUND( sum(p.crsale),2) as NUM_cr_sal,
                    ROUND( sum(COALESCE(p.crdisc , 0::numeric)),2) as NUM_cr_disc,
                    ROUND(COALESCE(s.um_cashtotal, 0::numeric),2) AS NUM_cashinhand,
                    ROUND(COALESCE(s.um_cashtotal, 0::numeric) - sum(p.um_cash),2) AS NUM_ex_sh,count(p.billcnt) AS INT_bills FROM ( 
                    select a.ad_client_id, a.ad_org_id, a.datetrx, a.c_pos_id,a.ad_user_id,a.billcnt,a.documentno,
                    case when a.pay_rank=1 then a.payamt  else 0 end as payamt,case when a.pay_rank=1 then a.um_cash  else 0 end as um_cash,
                    case when a.pay_rank=1 then a.um_creditcard  else 0 end as um_creditcard,case when a.pay_rank=1 then a.crsale  else 0 end as crsale,
                    case when a.pay_rank=1 then a.writeoffamt  else 0 end as writeoffamt,case when a.pay_rank=1 then a.sodx  else 0 end as sodx,
                    case when a.pay_rank=1 then a.um_voucher  else 0 end as um_voucher,case when a.pay_rank=1 then a.pgiftcard  else 0 end as pgiftcard,
                    case when a.pay_rank=1 then a.ticket  else 0 end as ticket,case when a.pay_rank=1 then a.lrvvoc  else 0 end as lrvvoc,
                    case when a.pay_rank=1 then a.phonepe  else 0 end as phonepe,case when a.pay_rank=1 then a.googlepay  else 0 end as googlepay,
                    case when a.pay_rank=1 then a.loycoupon  else 0 end as loycoupon,case when a.pay_rank=1 then a.ParkingTKN  else 0 end as ParkingTKN,
                    case when a.pay_rank=1 then a.upipayment  else 0 end as upipayment,case when a.pay_rank=1 then a.giftpass  else 0 end as giftpass,
                    case when a.pay_rank=1 then a.paytm  else 0 end as paytm,case when a.pay_rank=1 then a.othercpn  else 0 end as othercpn,
                    case when a.pay_rank=1 then a.txpress else 0 end as txpress,case when a.pay_rank=1 then a.razorpay  else 0 end as razorpay,
                    case when a.pay_rank=1 then a.advpaid else 0 end as advpaid,
                    case when a.pay_rank=1 then a.cashDisc  else 0 end as cashDisc,
                    case when a.pay_rank=1 then a.um_exchangeamt  else 0 end as um_exchangeamt,
                    case when a.pay_rank=1 then a.crdisc  else 0 end as crdisc from (
                    with payline as (select c_payment_id,sum(case when um_paymodename::text = 'Sodexo'::text  then payamt end) as sodx,
                    sum(case when um_paymodename::text = 'PGift Card'::text  then payamt end) as pgiftcard,
                    sum(case when um_paymodename::text = 'Ticket'::text  then payamt end) as ticket,
                    sum(case when um_paymodename::text = 'LS-LRV Voucher'::text  then payamt end ) as lrvvoc,
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
                    sum(case when um_paymodename::text = 'AdvPaid'::text  then payamt end) as advpaid,
                    sum(case when um_paymode_id=100  then pl.payamt end )as cashDisc from um_paymentline pl group by c_payment_id)
                    SELECT i.ad_client_id, i.ad_org_id, trunc(i.dateinvoiced::timestamp with time zone) AS datetrx,
                    COALESCE(i.c_pos_id, ( SELECT c_pos.c_pos_id FROM c_pos WHERE c_pos.name::text = i.terminal::text)) AS c_pos_id,i.um_cashier_id as ad_user_id,
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then p1.payamt else p.payamt END as payamt,1::numeric AS billcnt,i.documentno,
                    CASE 
                    WHEN (cd.docsubtypeso='WI' and COALESCE(pa.c_paymentallocate_id,0)>0) 
                    then (i.grandtotal - COALESCE(i.um_round_off,0) -coalesce(pll1.payamt,0::numeric)) 
                    WHEN (cd.docsubtypeso='WI' and COALESCE(pa.c_paymentallocate_id,0)=0) 
                    then (i.grandtotal - COALESCE(i.um_round_off,0) -coalesce(pll.payamt,0::numeric)) 
                    ELSE 0::numeric  
                    END as crsale,
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then p1.um_cash else p.um_cash END as um_cash, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then p1.um_coupon else p.um_coupon END as um_voucher, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then p1.um_creditcard else p.um_creditcard END as um_creditcard, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then round(p1.writeoffamt, 2) else round(p.writeoffamt, 2) END as writeoffamt, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.sodx else pl.sodx END as sodx, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.pgiftcard else pl.pgiftcard END as pgiftcard, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.ticket else pl.ticket END as ticket, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.lrvvoc else pl.lrvvoc END as lrvvoc, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.phonepe else pl.phonepe END as phonepe,
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.googlepay else pl.googlepay END as googlepay, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.loycoupon else pl.loycoupon END as loycoupon, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.ParkingTKN else pl.ParkingTKN END as ParkingTKN, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.giftpass else pl.giftpass END as giftpass, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.paytm else pl.paytm END as paytm, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.othercpn else pl.othercpn END as othercpn, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.txpress else pl.txpress END as txpress, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.upipayment else pl.upipayment END as upipayment, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.razorpay else pl.razorpay END as razorpay, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.advpaid else pl.advpaid END as advpaid, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then pl1.cashDisc else pl.cashDisc END as cashDisc, 
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then p1.um_exchangeamt else p.um_exchangeamt END as um_exchangeamt,
                    case 
                    when (cd.docsubtypeso='WI' and COALESCE(pa.c_paymentallocate_id,0)>0) then coalesce(pll1.payamt,0::numeric)  
                    when (cd.docsubtypeso='WI' and COALESCE(pa.c_paymentallocate_id,0)=0) then coalesce(pll.payamt,0::numeric) ELSE 0::numeric 
                    END as crdisc,
                    case when COALESCE(pa.c_paymentallocate_id,0)>0 then rank()over(partition by p1.c_payment_id order by i.c_invoice_id) 
                    when (COALESCE(pa.c_paymentallocate_id,0)=0 and p.c_payment_id>0) then  rank()over(partition by p.c_payment_id order by i.c_invoice_id)
                    else 1 end as pay_rank FROM c_invoice i
                    LEFT JOIN c_paymentallocate pa ON (i.c_invoice_id = pa.c_invoice_id)
                    LEFT JOIN c_payment p1 ON (pa.c_payment_id = p1.c_payment_id AND p1.c_doctype_id=1000051)
                    LEFT JOIN c_payment cp1 ON (pa.c_payment_id = cp1.c_payment_id AND cp1.c_doctype_id<>1000051 
                    and cp1.c_payment_id=(select min(c_payment_id) from c_payment cpp1 where cpp1.c_invoice_id=i.c_invoice_id))
                    LEFT JOIN c_payment p ON (i.c_invoice_id = p.c_invoice_id AND p.c_doctype_id=1000051)
                    LEFT JOIN c_payment cp ON (i.c_invoice_id = cp.c_invoice_id AND cp.c_doctype_id<>1000051 
                    and cp.c_payment_id=(select min(c_payment_id) from c_payment cpp where cpp.c_invoice_id=i.c_invoice_id))
                    LEFT JOIN um_paymentline pll ON (pll.c_payment_id = cp.c_payment_id)
                    LEFT JOIN payline pl ON pl.c_payment_id = p.c_payment_id
                    LEFT JOIN um_paymentline pll1 ON (pll1.c_payment_id = cp1.c_payment_id)
                    LEFT JOIN payline pl1 ON pl1.c_payment_id = p1.c_payment_id
                    LEFT JOIN c_order o ON o.c_order_id = i.c_order_id
                    left join c_doctype cd on cd.c_doctype_id=o.c_doctype_id
                    WHERE i.dateinvoiced::date >= '%s' and  i.dateinvoiced::date <='%s' AND i.issotrx = 'Y'::bpchar AND (i.c_pos_id > 0::numeric OR i.terminal IS NOT NULL) AND (i.docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar]))
                    GROUP BY i.ad_client_id, i.ad_org_id,i.um_cashier_id, i.dateinvoiced, i.c_pos_id, p.payamt,pll.payamt, p.um_cash, p.um_coupon, p.um_creditcard, i.documentno, i.grandtotal,i.um_round_off,p.writeoffamt,i.terminal,p.c_payment_id,i.c_doctype_id,pl.sodx,pl.pgiftcard,pl.ticket,pl.lrvvoc,pl.phonepe,pl.googlepay,
                    pl.loycoupon,pl.ParkingTKN,pl.giftpass,pl.paytm,pl.othercpn,pl.txpress,pl.upipayment,pl.razorpay,pl.cashDisc,docsubtypeso,p.um_exchangeamt,pl.advpaid,
                    p.c_invoice_id,p1.um_cash,p1.um_coupon,p1.um_creditcard,p1.writeoffamt,pl1.sodx,pl1.pgiftcard,pl1.ticket,pl1.lrvvoc,pl1.phonepe,pl1.googlepay,pl1.loycoupon,
                    pl1.ParkingTKN,pl1.giftpass,pl1.paytm,pl1.othercpn,pl1.txpress,pl1.upipayment,pl1.razorpay,pl1.advpaid,pl1.cashDisc,p1.um_exchangeamt,pl1.advpaid,
                    pa.c_paymentallocate_id,pll1.payamt,i.c_invoice_id,p1.c_payment_id,p1.payamt ORDER BY i.dateinvoiced DESC)a ) p
                    inner join c_pos pos on (pos.c_pos_id = p.c_pos_id)
                    inner join ad_user u on (u.ad_user_id=p.ad_user_id)
                    LEFT JOIN um_settlement s ON s.c_pos_id = p.c_pos_id AND s.um_settlementdate = p.datetrx and s.salesrep_id=p.ad_user_id
                    GROUP BY p.ad_client_id, p.ad_org_id, pos.c_pos_id,pos.name, p.datetrx, s.um_cashtotal ,u.name
                    )) r group by r.grp_date,r.pos,r.cashier Order by r.grp_date 
    
    
    
                      '''  %(start_date,end_date,start_date,end_date)
                                  
                cursor.execute(sql)
                sale_data = cursor.fetchall()
                for row in sale_data:                
                        dict = {'date':row[0],'pos':row[1] ,'cashier':row[2],'sale_amount':row[3] ,'cash':row[4] ,
                                'ccard':row[5] ,'voucher':row[6] ,'sodexo':row[7] ,'gift':row[8],'lrvvoc':row[9] ,
                                 'phonepe':row[10],'googlepay':row[11] , 
                                'loycoupon':row[12] ,'parkingtkn':row[13] ,'giftpass':row[14] ,
                                'paytm':row[15],'othercpn':row[16] , 'ticket':row[17],'txpress':row[18] ,
                                'upipayment':row[19] ,
                                'razorpay':row[20] ,'advpaid':row[21] ,'cashdisc':row[22] ,
                                'cr_sal':row[23] ,
                                 'cr_disc':row[24],'cashinhand':row[25] ,'ex_sh':row[26] ,'bills':row[27] ,}
                        
                        lis.append(dict)
                return lis
            except (Exception, psycopg2.Error) as error:
                if not sale_data:
                    raise UserError(_('No data available for the input specified search criteria'))

            finally:
    # closing database connection.
                if db_conn:
                    cursor.close()
                    db_connect.close()
              
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
        advpaid_sum_amt= 0
        cashdisc_sum_amt= 0
        cr_sal_sum_amt= 0
        cr_disc_sum_amt= 0
        ex_sh_sum_amt= 0
        summary_sale_order_line = []
        bill_sum_amt = 0
        for line in get_lines(self):
            if line['pos']:
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
                if line['advpaid']:
                    advpaid_sum_amt+=line['advpaid'] 
                if line['cashdisc']:
                    cashdisc_sum_amt+=line['cashdisc'] 
                if line['cr_sal']:
                    cr_sal_sum_amt+=line['cr_sal'] 
                if line['cr_disc']:
                    cr_disc_sum_amt+=line['cr_disc'] 
                if line['ex_sh']:
                    ex_sh_sum_amt+=line['ex_sh'] 
            summary_sale_order_line.append((0,0,{
                                    'date' : line['date'],
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
          
                                   
                                         }))
        if  summary_sale_order_line:
            summary_sale_order_line.append((0,0,{
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
                    'advpaid': advpaid_sum_amt,
                    'cashdisc' : cashdisc_sum_amt,
                     'cr_sal' : cr_sal_sum_amt,
                     'cr_disc' :cr_disc_sum_amt,
                      'ex_sh' :ex_sh_sum_amt,
                }))
                                   
        vals = {
               'start_date' : self.start_date,
               'end_date' : self.end_date,
               'company_id' : self.company_id.name,
                'summary_sale_order_line': summary_sale_order_line, 
                }
        sales_summary_reports_id = self.env['sales.summary.screen.wzd'].create(vals)

        res = self.env['ir.model.data'].check_object_reference(
                                            'ls_pos_reports', 'view_summary_order_wzd_report')
        return {
                    'name': 'Sales Summary Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sales.summary.screen.wzd',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': sales_summary_reports_id.id,
            }
       
class summary_sales_screen_wzd(models.Model):
    _name = "sales.summary.screen.wzd"
    _description = "Summary Sale Reports"
    
    name = fields.Char(default="Sales Summary Report")
    summary_sale_order_line = fields.One2many('sales.summary.screen.line','department_id',string='Open Order Line')
    start_date = fields.Date('Date From')
    end_date = fields.Date('Date To') 
    company_id = fields.Char("Company")
    
    def print_open_orders_excel_report(self):
        filename= 'Sales Summary Report.xls'
        workbook= xlwt.Workbook(encoding="UTF-8")
        
        
        style_header = xlwt.easyxf('pattern: pattern solid, fore_colour light_orange;'
                               'font: bold on; font:height 230; align: wrap No; borders: left thin, right thin, top thin, bottom thin;')
        style = xlwt.easyxf('font:height 230; align: wrap No;borders: left thin, right thin, top thin, bottom thin;')
        header=xlwt.easyxf('pattern: pattern solid, fore_colour light_orange;''font:height 400; align: horiz center;font:bold True;' "borders: top thin,bottom thin , left thin, right thin")
        style = xlwt.easyxf('font:height 230; align: wrap No;')
        base_style = xlwt.easyxf('align: wrap yes')
        date_style = xlwt.easyxf('align: wrap yes', num_format_str='DD-MM-YYYY')
        datetime_style = xlwt.easyxf('align: wrap yes', num_format_str='DD-MM-YYYY HH:mm:SS')
        sheet= workbook.add_sheet('Summary Sales Report')
        format6 = xlwt.easyxf('pattern: pattern solid, fore_colour light_yellow;''font:height 280,bold True;align: horiz left;'"borders: top thin,bottom thin , left thin, right thin")
        format7 = xlwt.easyxf('pattern: pattern solid, fore_colour light_yellow;''font:height 280,bold True;align: horiz center;'"borders: top thin,bottom thin , left thin, right thin")
        format1 = xlwt.easyxf('font: bold off, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color white;')
        my_format = xlwt.easyxf(num_format_str= '0.00')
        start_date = self.start_date  or ''
        end_date = self.end_date or ''
        company_id = self.company_id or ''   
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
        sheet.write(2, 2, 'cashier', format7)
        sheet.write(2, 3, 'Sales Amount', format7)
        sheet.write(2, 4, 'Cash', format7)
        sheet.write(2, 5, 'ccard', format7)
        sheet.write(2, 6, 'Voucher', format7)
        sheet.write(2, 7, 'sodexo', format7)
        sheet.write(2, 8,'gift',format7)
        sheet.write(2, 9, 'Irvvoc', format7)
        sheet.write(2, 10, 'Phonepe', format7)
        sheet.write(2, 11, 'Google Pay', format7)
        sheet.write(2, 12, 'loycoupon', format7)
        sheet.write(2, 13, 'parkingtkn', format7)
        sheet.write(2, 14, 'Giftpass', format7)
        sheet.write(2, 15, 'Paytm', format7)
        sheet.write(2, 16, 'othercpn', format7)
        sheet.write(2, 17, 'Ticket', format7)
        sheet.write(2, 18, 'txpress', format7)
        sheet.write(2, 19,'upipayment',format7)
        sheet.write(2, 20, 'razorpay', format7)
        sheet.write(2, 21, 'advpaid', format7)
        sheet.write(2, 22, 'cashdisc', format7)
        sheet.write(2, 23, 'cr_sal', format7)
        sheet.write(2, 24, 'cr_disc', format7)
        sheet.write(2, 25, 'cashinhand', format7)
        sheet.write(2, 26, 'ex_sh', format7)
        sheet.write(2, 27, 'bills', format7)
        sheet.write_merge(0, 1, 0, 8, 'Summary Sales Report',header) 
   
        
               
        sql = '''
                select to_char(date,'dd/mm/yyyy'),pos,cashier,sale_amount,cash,
                    ccard,voucher,sodexo,gift,lrvvoc,
                     phonepe,googlepay,loycoupon,parkingtkn,
                     giftpass,paytm,othercpn,ticket,txpress,
                     upipayment,razorpay,advpaid,cashdisc,
                     cr_sal,cr_disc,cashinhand ,ex_sh,bills from
                    sales_summary_screen_line         
                    where department_id=(select max(department_id) from sales_summary_screen_line)                              
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
        export_id = self.env['excel.extended.summary.rep'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        
        fp.seek(0)
        data = fp.read()
        fp.close()

        return{
              'view_mode': 'form',
              'res_id': export_id.id,
              'res_model': 'excel.extended.summary.rep',
              'type': 'ir.actions.act_window',
              'context': False,
          
            }
        
summary_sales_screen_wzd()
 
class summary_sale_screen_line(models.Model):
    _name = "sales.summary.screen.line"
    _description = "Sales summary Line"
    
    department_id = fields.Many2one('sales.summary.screen.wzd',string='department_id',ondelete='cascade')
    date = fields.Date('Date')
    pos = fields.Char('POS')
    cashier = fields.Char('cashier')
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
    advpaid = fields.Char('advpaid')
    cashdisc = fields.Float('cashdisc')
    cr_sal = fields.Float('cr_sal')
    cr_disc = fields.Float('cr_disc')
    cashinhand = fields.Float('cashinhand')
    ex_sh = fields.Float('ex_sh')
    bills = fields.Float('bills')
           
summary_sale_screen_line()
    
     
class excel_extended_sales_open_orders_rep(models.Model):
    _name= "excel.extended.summary.rep"
    
    name = fields.Char(default="Summary Sales Report")
    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64) 
    
    