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
import timeit

DATE_FORMAT_1 = "%Y-%d-%m"
DATE_FORMAT_2 = "%d/%m/%y"
DATE_FORMAT_3 = "%m/%d/%y"


class cashier_sales_details_wzd(models.Model):
    _name = "cashier.sales.report.ss"
       
    start_date = fields.Date('Date From') 
    end_date = fields.Date(string="Date To") 
    company_id = fields.Many2one('res.company',string='Company',default=lambda self:self.env.company.id)
            
    def print_cashier_sales_report(self):
        start=timeit.default_timer() 
        def get_cashier_lines(self):
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
                self.env['cashier.sales.report.screen.line.ss'].search([]).unlink()
                   
                sql='''
              select 
                case when STR_TenderType is null then null else grp_datetrx::date end as grp_datetrx,grp_name,
               str_tendertype,round(SUM_amt,2) as sum_amt from   
               ( select   datetrx::date   as grp_datetrx,
 name as grp_name,
    TenderType as STR_TenderType, sum(amt) as SUM_amt from (
  select  
    p.datetrx , u.name ,'Cash Amt' as TenderType, sum(p.um_cash) as amt from  c_payment p
   JOIN c_invoice i ON i.c_invoice_id = p.c_invoice_id
   LEFT JOIN c_order o ON o.c_order_id = i.c_order_id
   inner join ad_user u on (u.ad_user_id=i.createdby)
  WHERE i.issotrx = 'Y'::bpchar AND (o.c_pos_id > 0::numeric OR i.terminal IS NOT NULL) 
  AND (i.docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar]))
  group by p.datetrx,u.name 
  UNION ALL
   select  
    p.datetrx , u.name , 'Voucher Amt' as TenderType, sum(p.um_coupon) as amt from  c_payment p
   JOIN c_invoice i ON i.c_invoice_id = p.c_invoice_id
   LEFT JOIN c_order o ON o.c_order_id = i.c_order_id
   inner join ad_user u on (u.ad_user_id=i.createdby)
  WHERE i.issotrx = 'Y'::bpchar AND (o.c_pos_id > 0::numeric OR i.terminal IS NOT NULL) 
  AND (i.docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar]))
  group by p.datetrx,u.name 
    UNION ALL
   select  
    p.datetrx , u.name ,'Card Amt' as TenderType, sum(p.um_creditcard) as amt from  c_payment p
   JOIN c_invoice i ON i.c_invoice_id = p.c_invoice_id
   LEFT JOIN c_order o ON o.c_order_id = i.c_order_id
   inner join ad_user u on (u.ad_user_id=i.createdby)
  WHERE i.issotrx = 'Y'::bpchar AND (o.c_pos_id > 0::numeric OR i.terminal IS NOT NULL) 
  AND (i.docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar]))
  group by p.datetrx,u.name 
  UNION ALL
select p.datetrx , u.name ,pm.um_paymodename as TenderType, sum(pl.payamt) as amt from  c_payment p
   JOIN c_invoice i ON i.c_invoice_id = p.c_invoice_id 
   Join UM_PaymentLine pl on (pl.C_Payment_ID=p.C_Payment_ID)
   JOIN UM_PayMode pm on pm.um_paymode_id=pl.um_paymode_id
    LEFT JOIN c_order o ON o.c_order_id = i.c_order_id
    left join c_doctype cd on cd.c_doctype_id=o.c_doctype_id
   inner join ad_user u on (u.ad_user_id=i.createdby)
  WHERE i.issotrx = 'Y'::bpchar AND (o.c_pos_id > 0::numeric OR i.terminal IS NOT NULL) 
  AND (i.docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar])) AND cd.docsubtypeSO<>'WI' 
  group by p.datetrx,u.name,pm.um_paymodename
  Union ALL 
  select  i.dateinvoiced as datetrx , u.name ,'Credit Sale' as TenderType, 
  sum(i.grandtotal-coalesce(i.um_round_off,0::numeric)-coalesce(pl.payamt,0)) as amt from  c_invoice i
   LEFT JOIN c_order o ON o.c_order_id = i.c_order_id
   left join c_doctype cd on cd.c_doctype_id=o.c_doctype_id
   LEFT JOIN c_payment p ON (i.c_invoice_id = p.c_invoice_id AND 
   p.c_payment_id=(select min(c_payment_id) from c_payment cpp where cpp.c_invoice_id=i.c_invoice_id))
   LEFT Join UM_PaymentLine pl on (pl.C_Payment_ID=p.C_Payment_ID)
   inner join ad_user u on (u.ad_user_id=i.createdby)
  WHERE i.issotrx = 'Y'::bpchar AND (o.c_pos_id > 0::numeric OR i.terminal IS NOT NULL) AND cd.docsubtypeSO='WI' 
  AND (i.docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar]))
  group by i.dateinvoiced,u.name 
  UNION ALL
  select p.datetrx , u.name ,'Credit Disc' as TenderType, sum(pl.payamt) as amt from  c_payment p
   JOIN c_invoice i ON i.c_invoice_id = p.c_invoice_id 
   Join UM_PaymentLine pl on (pl.C_Payment_ID=p.C_Payment_ID)
   JOIN UM_PayMode pm on pm.um_paymode_id=pl.um_paymode_id
    LEFT JOIN c_order o ON o.c_order_id = i.c_order_id
    left join c_doctype cd on cd.c_doctype_id=o.c_doctype_id 
   inner join ad_user u on (u.ad_user_id=i.createdby)
  WHERE i.issotrx = 'Y'::bpchar AND (o.c_pos_id > 0::numeric OR i.terminal IS NOT NULL) and  cd.docsubtypeSO='WI'
  AND (i.docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar]))
  group by p.datetrx,u.name,pm.um_paymodename )
  c WHERE c.datetrx::date >= '%s' and  c.datetrx::date <='%s' 
                group by c.datetrx,c.name,c.tendertype
  union all
           select   datetrx::date   as grp_datetrx,
 name as grp_name,
    null as STR_TenderType, sum(amt) as SUM_amt from (
  select  
    p.datetrx , u.name ,'Cash Amt' as TenderType, sum(p.um_cash) as amt from  c_payment p
   JOIN c_invoice i ON i.c_invoice_id = p.c_invoice_id
   LEFT JOIN c_order o ON o.c_order_id = i.c_order_id
   inner join ad_user u on (u.ad_user_id=i.createdby)
  WHERE i.issotrx = 'Y'::bpchar AND (o.c_pos_id > 0::numeric OR i.terminal IS NOT NULL) 
  AND (i.docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar]))
  group by p.datetrx,u.name 
  UNION ALL
   select  
    p.datetrx , u.name , 'Voucher Amt' as TenderType, sum(p.um_coupon) as amt from  c_payment p
   JOIN c_invoice i ON i.c_invoice_id = p.c_invoice_id
   LEFT JOIN c_order o ON o.c_order_id = i.c_order_id
   inner join ad_user u on (u.ad_user_id=i.createdby)
  WHERE i.issotrx = 'Y'::bpchar AND (o.c_pos_id > 0::numeric OR i.terminal IS NOT NULL) 
  AND (i.docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar]))
  group by p.datetrx,u.name 
    UNION ALL
   select  
    p.datetrx , u.name ,'Card Amt' as TenderType, sum(p.um_creditcard) as amt from  c_payment p
   JOIN c_invoice i ON i.c_invoice_id = p.c_invoice_id
   LEFT JOIN c_order o ON o.c_order_id = i.c_order_id
   inner join ad_user u on (u.ad_user_id=i.createdby)
  WHERE i.issotrx = 'Y'::bpchar AND (o.c_pos_id > 0::numeric OR i.terminal IS NOT NULL) 
  AND (i.docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar]))
  group by p.datetrx,u.name 
  UNION ALL
select p.datetrx , u.name ,null as TenderType, sum(pl.payamt) as amt from  c_payment p
   JOIN c_invoice i ON i.c_invoice_id = p.c_invoice_id 
   Join UM_PaymentLine pl on (pl.C_Payment_ID=p.C_Payment_ID)
   JOIN UM_PayMode pm on pm.um_paymode_id=pl.um_paymode_id
    LEFT JOIN c_order o ON o.c_order_id = i.c_order_id
    left join c_doctype cd on cd.c_doctype_id=o.c_doctype_id
   inner join ad_user u on (u.ad_user_id=i.createdby)
  WHERE i.issotrx = 'Y'::bpchar AND (o.c_pos_id > 0::numeric OR i.terminal IS NOT NULL) 
  AND (i.docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar])) AND cd.docsubtypeSO<>'WI' 
  group by p.datetrx,u.name,pm.um_paymodename
  Union ALL 
  select  i.dateinvoiced as datetrx , u.name ,'Credit Sale' as TenderType, 
  sum(i.grandtotal-coalesce(i.um_round_off,0::numeric)-coalesce(pl.payamt,0)) as amt from  c_invoice i
   LEFT JOIN c_order o ON o.c_order_id = i.c_order_id
   left join c_doctype cd on cd.c_doctype_id=o.c_doctype_id
   LEFT JOIN c_payment p ON (i.c_invoice_id = p.c_invoice_id AND 
   p.c_payment_id=(select min(c_payment_id) from c_payment cpp where cpp.c_invoice_id=i.c_invoice_id))
   LEFT Join UM_PaymentLine pl on (pl.C_Payment_ID=p.C_Payment_ID)
   inner join ad_user u on (u.ad_user_id=i.createdby)
  WHERE i.issotrx = 'Y'::bpchar AND (o.c_pos_id > 0::numeric OR i.terminal IS NOT NULL) AND cd.docsubtypeSO='WI' 
  AND (i.docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar]))
  group by i.dateinvoiced,u.name 
  UNION ALL
  select p.datetrx , u.name ,'Credit Disc' as TenderType, sum(pl.payamt) as amt from  c_payment p
   JOIN c_invoice i ON i.c_invoice_id = p.c_invoice_id 
   Join UM_PaymentLine pl on (pl.C_Payment_ID=p.C_Payment_ID)
   JOIN UM_PayMode pm on pm.um_paymode_id=pl.um_paymode_id
    LEFT JOIN c_order o ON o.c_order_id = i.c_order_id
    left join c_doctype cd on cd.c_doctype_id=o.c_doctype_id 
   inner join ad_user u on (u.ad_user_id=i.createdby)
  WHERE i.issotrx = 'Y'::bpchar AND (o.c_pos_id > 0::numeric OR i.terminal IS NOT NULL) and  cd.docsubtypeSO='WI'
  AND (i.docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar]))
  group by p.datetrx,u.name,pm.um_paymodename )
  c WHERE c.datetrx::date >= '%s' and  c.datetrx::date <='%s' 
               group by c.datetrx,c.name)k 
order by k.grp_datetrx,k.grp_name,k.str_tendertype
        '''  %(start_date, end_date,start_date, end_date)
                
                stop = timeit.default_timer()
                
                cursor.execute(sql)
                sale_data = cursor.fetchall()
                
                st = timeit.default_timer()
                return sale_data
            except (Exception, psycopg2.Error) as error:
                raise UserError(_("Error while fetching data from PostgreSQL "))
              
            finally:
                if db_conn:
                    cursor.close() 
                    db_connect.close()
                   
              
           
        tamt = 0

        cashier_sale_line = []
        seq = 0
        
        st=timeit.default_timer() 
        
        for line in get_cashier_lines(self): 
            if line[2]:
                tamt+=line[3] 

            cashier_sale_line.append((0,0,{
                                'date' : line[0],
                                'name' : line[1],
                                'tender_type' : line[2],
                                'amt' : line[3],
                                  
                              
                                     }))
        if cashier_sale_line:
            cashier_sale_line.append((0,0,{   
                                    'amt' : tamt, 
                                 }))    
                
            
         
        vals = { 
                'start_date':self.start_date,             
                'end_date': self.end_date,
                'company_id' : self.company_id.name,
                'cashier_sale_line': cashier_sale_line, 
                }
        valst = timeit.default_timer()
        print("vals Run Time = ", valst - st)
        
        sales_wise_reports_id = self.env['cashier.sales.report.screen.wzd.ss'].create(vals)

        res = self.env['ir.model.data'].check_object_reference(
                                           'ss_pos_reports', 'view_cashier_wzd_report')
        creatst = timeit.default_timer()
        print("create Run Time = ", creatst - valst)
        
        return {
                    'name': 'Cashier Sales Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'cashier.sales.report.screen.wzd.ss',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': sales_wise_reports_id.id,
            }
       
       
class cashier_sales_screen_wzd(models.Model):
    _name = "cashier.sales.report.screen.wzd.ss"
    _description = "Cashier wise Sales Reports"
    
    name = fields.Char(string="Name", default='Cashier wise Sales Report')
    start_date = fields.Date(string="Date From")
    end_date = fields.Date(string="Date To")
    company_id = fields.Char("Company")
    cashier_sale_line = fields.One2many('cashier.sales.report.screen.line.ss','cashier_order_id',string='Open Order Line')
    
    def print_cashier_excel_report(self):
        filename= 'Cashier Wise Sales Report.xls'
        workbook= xlwt.Workbook(encoding="UTF-8")
        style_header = xlwt.easyxf('font: bold on; font:height 230; align: wrap No; borders: left thin, right thin, top thin, bottom thin;')
        style = xlwt.easyxf('font:height 230; align: wrap No;borders: left thin, right thin, top thin, bottom thin;')
        header=xlwt.easyxf('pattern: pattern solid, fore_colour light_orange;''font:height 400; align: horiz center;font:bold True;' "borders: top thin,bottom thin , left thin, right thin")
        style = xlwt.easyxf('font:height 230; align: wrap No;')
        base_style = xlwt.easyxf('align: wrap yes')
        date_style = xlwt.easyxf('align: wrap yes', num_format_str='DD-MM-YYYY')
        datetime_style = xlwt.easyxf('align: wrap yes', num_format_str='DD-MM-YYYY HH:mm:SS')
        sheet= workbook.add_sheet('Cashier wise Sales Report')
        format6 = xlwt.easyxf('font:height 210,bold True;align: horiz left')
        
        format7 = xlwt.easyxf('font: bold off, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color yellow;')
        txt_v = xlwt.easyxf('font: bold off, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color white;')
        start_date = self.start_date or ''
        end_date = self.end_date  or ''
        company_id = self.company_id  or ''
        

        sheet.col(0).width = 850*5
        sheet.col(1).width = 850*5
        sheet.col(2).width = 850*5
        sheet.col(3).width = 850*5
        sheet.col(4).width = 850*5
        sheet.col(5).width = 850*5
        sheet.col(6).width = 850*5
        sheet.col(7).width = 850*5
        sheet.col(8).width = 850*5
        sheet.col(9).width = 850*5
        sheet.col(10).width = 850*5    
        sheet.col(11).width = 850*5
        sheet.write(2, 0, 'Date', format6)
        sheet.write(2, 1, 'Name', format6)
        sheet.write(2, 2, 'Tender Type', format6)
        sheet.write(2, 3, 'Quantity', format6)
                  
        sheet.write_merge(0, 1, 0, 3, 'Cashier Sales Report',header)
           
               
        sql = '''    
                 select to_char(date,'dd/mm/yyyy'), name, tender_type, amt  from cashier_sales_report_screen_line_ss
                where cashier_order_id=(select max(cashier_order_id) from cashier_sales_report_screen_line_ss)    
               
              
                     '''
           

           
        self.env.cr.execute(sql)
        rows2 = self.env.cr.fetchall()
        for row_index, row in enumerate(rows2):
            for cell_index, cell_value in enumerate(row):
                cell_style = txt_v 
                if isinstance(cell_value, str):
                    cell_value = re.sub("\r", " ", cell_value)
                elif isinstance(cell_value,float) :
                    cell_style =  txt_v    
                sheet.row(row_index+1).height = 70*5
                sheet.write(row_index + 3, cell_index, cell_value,txt_v)
                     
        fp =io.BytesIO()
        workbook.save(fp)
        export_id = self.env['excel.extended.cashier.sales.rep.ss'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        
        fp.seek(0)
        data = fp.read()
        fp.close()

        return{
              'view_mode': 'form',
              'res_id': export_id.id,
              'res_model': 'excel.extended.cashier.sales.rep.ss',
              'type': 'ir.actions.act_window',
              'context': False, 
          
            }
        
cashier_sales_screen_wzd()
 
class cashier_sales_screen_line(models.Model):
    _name = "cashier.sales.report.screen.line.ss"
    _description = "Open Orders summary Line"
    
    cashier_order_id = fields.Many2one('cashier.sales.report.screen.wzd.ss',string='cashier_order_id',ondelete='cascade')
    date = fields.Date(string="Date")
    name = fields.Char(string="Name")
    tender_type = fields.Char(string="Tender Type")
    amt = fields.Float(string="Amount")
    
           
cashier_sales_screen_line()

     
class excel_extended_cashier_saless_rep(models.Model):
    _name= "excel.extended.cashier.sales.rep.ss"

    name = fields.Char(string="Name", default='Download Excel Report')    
    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64) 
    
    
