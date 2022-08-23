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

DATE_FORMAT_1 = "%d-%m-%y"
DATE_FORMAT_2 = "%d/%m/%y"
DATE_FORMAT_3 = "%d/%m/%y"


class ss_total_sales_details_wzd(models.Model):
    _name = "ss.total.sales.report"
    
       
    start_date = fields.Date('Date From') 
    end_date = fields.Date('Date To')
    company_id = fields.Many2one('res.company',string='Company',default=lambda self:self.env.company.id)
    online_sales = fields.Boolean('Online Sales Only')
            
    def print_ss_totalsales_report(self):
        def get_total_lines(self):
            lis = []
            start_date = self.start_date
            end_date = self.end_date
            company_id = self.company_id.name
            online_sales = self.online_sales
            
            
            try:
                db_conn = self.env['db.connection'].search([('company_id', '=', self.company_id.name)], limit=1)
                db_connect = db_conn.database_connect()
                cursor = db_connect.cursor() 
                self.env['ss.total.sales.line'].search([]).unlink()
                sql = '''
                      SELECT  sal.datetrx,sum(sal.grandtotal) AS NUM_total_salesamt, 0 as NUM_discountamt, 
sum(sal.writeoffamt)+sum(sal.um_round_off) AS NUM_roundoff,
 round(sum(sal.grandtotal) - sum(sal.writeoffamt) - sum(sal.um_round_off), 2) AS NUM_total_netamt, 
count(sal.billcnt) AS int_bill_count,
round(round(sum(sal.grandtotal) - sum(sal.writeoffamt), 2) / count(sal.billcnt)::numeric, 2) AS avgbill from
(
SELECT i.ad_client_id, i.ad_org_id, trunc(i.dateinvoiced::timestamp with time zone) AS datetrx,
 COALESCE(o.c_pos_id, ( SELECT c_pos.c_pos_id      FROM c_pos
          WHERE c_pos.name::text = i.terminal::text)) AS c_pos_id, 
p.um_cash, p.um_coupon AS um_voucher, p.um_creditcard, i.documentno, 
i.grandtotal as grandtotal,coalesce(i.um_round_off,0::numeric) as um_round_off, 1::numeric AS billcnt,
case when p.c_doctype_id = 1000051 then round(p.writeoffamt, 2)
else 0 end AS writeoffamt
   FROM c_invoice i
   LEFT JOIN c_payment p ON (i.c_invoice_id = p.c_invoice_id and p.c_payment_id=(select min(c_payment_id) from c_payment cpp where cpp.c_invoice_id=i.c_invoice_id))
   LEFT JOIN c_order o ON o.c_order_id = i.c_order_id
   LEFT JOIN um_paymentline pl ON pl.c_payment_id = p.c_payment_id
  WHERE   i.dateinvoiced::date >= '%s' and  i.dateinvoiced::date <='%s'  
and i.issotrx = 'Y'::bpchar AND (o.c_pos_id > 0::numeric OR i.terminal IS NOT NULL) AND (i.docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar]))
and ('N'=%s or i.um_onlinesales='Y')
  GROUP BY i.ad_client_id, i.ad_org_id, i.dateinvoiced, o.c_pos_id, p.payamt, p.um_cash, p.um_coupon, p.um_creditcard, i.documentno, i.grandtotal,i.um_round_off, p.writeoffamt, i.terminal, p.c_payment_id,i.c_doctype_id,p.c_doctype_id
  ORDER BY i.dateinvoiced DESC
) as sal
  GROUP BY sal.ad_client_id, sal.ad_org_id, sal.datetrx
  ORDER BY sal.datetrx                                  
                      ''' % (start_date, end_date,online_sales)
                             
                cursor.execute(sql)
                sale_data = cursor.fetchall()
                return sale_data
        
            except (Exception, psycopg2.Error) as error:
                raise UserError(_("Error while fetching data from PostgreSQL "))
 
            finally:  # closing database connection.
                if db_conn:
                    cursor.close()
                    db_connect.close()
        
        total_sales_amt_tot = 0
        dis_amt_tot = 0
        round_off_tot = 0
        tot_net_amt_tot = 0
        bill_count_tot = 0
        ss_total_sales_line = []
       
        
        for line in get_total_lines(self):
            if line[1]:
                total_sales_amt_tot += line[1]
            if line[2]:
                dis_amt_tot += line[2]
            if line[3]:
                round_off_tot += line[3]
            if line[4]:
                tot_net_amt_tot += line[4]
            if line[5]:
                bill_count_tot += line[5]
                         
            ss_total_sales_line.append((0, 0, {
                                'datetrx': line[0],
                                'total_sales_amt': line[1],
                                'dis_amt': line[2],
                                'round_off': line[3],
                                'tot_net_amt': line[4],
                                'bill_count': line[5],
                                'avg_bill': line[6],
                                     }))
        if ss_total_sales_line:
            ss_total_sales_line.append((0, 0, {  
                                'total_sales_amt': total_sales_amt_tot,
                                'dis_amt': dis_amt_tot,
                                'round_off': round_off_tot,
                                'tot_net_amt': tot_net_amt_tot,
                                'bill_count': bill_count_tot,
                            }))    
         
        vals = {
               'start_date': self.start_date,
               'end_date': self.end_date,
               'company_id':self.company_id.name,
               'online_sales':self.online_sales,
               'ss_total_sales_line': ss_total_sales_line,
                }
       
        
        total_reports_id = self.env['ss.total.screen.wzd'].create(vals)
       
        res = self.env['ir.model.data'].check_object_reference(
                                            'ss_pos_reports', 'view_ss_total_sales_screen_wzd_report')
        
       
        return {
                    'name': 'Total sales Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'ss.total.screen.wzd',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': total_reports_id.id,
            }

       
class ss_total_sales_screen_wzd(models.Model):
    _name = "ss.total.screen.wzd"
    _description = "Total Sales Reports"
    
    name = fields.Char(default="Total Sales Report")
    ss_total_sales_line = fields.One2many('ss.total.sales.line', 'ss_total_sales_id')
    start_date = fields.Date('Date From')
    end_date = fields.Date('Date To')
    company_id = fields.Char('Company')
    online_sales = fields.Char('Online Sales Only')
    
    def print_sstotal_orders_excel_report(self):
        filename = 'Total Sales Report.xls'
        
        workbook = xlwt.Workbook(encoding="UTF-8")
        style_header = xlwt.easyxf('pattern: pattern solid, fore_colour light_orange;'
                               'font: bold on; font:height 230; align: wrap No; borders: left thin, right thin, top thin, bottom thin;')
        style = xlwt.easyxf('font:height 230; align: wrap No;borders: left thin, right thin, top thin, bottom thin;')
        header = xlwt.easyxf('pattern: pattern solid, fore_colour light_orange;''font:height 400; align: horiz center;font:bold True;' "borders: top thin,bottom thin , left thin, right thin")
        style = xlwt.easyxf('font:height 230; align: wrap No;')
        base_style = xlwt.easyxf('align: wrap yes')
        date_style = xlwt.easyxf('align: wrap yes', num_format_str='DD-MM-YYYY')
        datetime_style = xlwt.easyxf('align: wrap yes', num_format_str='DD-MM-YYYY HH:mm:SS')
        sheet = workbook.add_sheet('Total Sales Report')
        format6 = xlwt.easyxf('pattern: pattern solid, fore_colour light_yellow;''font:height 210,bold True;align: horiz left;'"borders: top thin,bottom thin , left thin, right thin")
        format7 = xlwt.easyxf("borders: top thin,bottom thin , left thin, right thin")
       
        format1 = xlwt.easyxf('font: bold off, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color white;')
        end_date = self.end_date  or ''
        start_date = self.start_date or ''
        company_id = self.company_id or ''
        online_sales = self.online_sales or ''
            
        sheet.col(0).width = 850 * 5 
        sheet.col(1).width = 850 * 5
        sheet.col(2).width = 850 * 5
        sheet.col(3).width = 850 * 5    
        sheet.col(4).width = 850 * 5 
        sheet.col(5).width = 850 * 5
        sheet.col(6).width = 850 * 5
        sheet.col(7).width = 850 * 5  
        sheet.write(2, 0, 'Datetrx', format6)
        sheet.write(2, 1, 'Total Sales Amt', format6)
        sheet.write(2, 2, 'Discount Amt', format6)
        sheet.write(2 , 3, 'RoundOff', format6)
        sheet.write(2, 4, 'Total Net Amt', format6)
        sheet.write(2, 5, 'Bil Count', format6)
        sheet.write(2, 6, 'Avg Bill', format6)
        sheet.write_merge(0, 1, 0, 6, 'Total Sales Report', header)
               
        sql = '''
            select 
                to_char(datetrx,'dd/mm/yyyy'),total_sales_amt,dis_amt,round_off,tot_net_amt,bill_count,avg_bill 
                from ss_total_sales_line         
                where ss_total_sales_id=(select max(ss_total_sales_id) from ss_total_sales_line)                 
            '''

        self.env.cr.execute(sql)
        rows2 = self.env.cr.fetchall()
        for row_index, row in enumerate(rows2):
            for cell_index, cell_value in enumerate(row):
                cell_style = format1 
                if isinstance(cell_value, str):
                    cell_value = re.sub("\r", " ", cell_value)
                elif isinstance(cell_value, float):
                    cell_style = format1   
                sheet.row(row_index + 1).height = 70 * 5
                sheet.write(row_index + 3, cell_index, cell_value, format1)
                      
        fp = io.BytesIO()
        workbook.save(fp)
        export_id = self.env['ss.excel.extended.total.rep'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        
        fp.seek(0)
        data = fp.read()
        fp.close()

        return{
              'view_mode': 'form',
              'res_id': export_id.id,
              'res_model': 'ss.excel.extended.total.rep',
              'type': 'ir.actions.act_window',
              'context': False,
          
            }

        
ss_total_sales_screen_wzd()

 
class ss_total_sales_screen_line(models.Model):
    _name = "ss.total.sales.line"
    _description = "Sales summary Line"
    
    ss_total_sales_id = fields.Many2one('ss.total.screen.wzd', string='ss_total_sales_id', ondelete='cascade')
    
    datetrx = fields.Date(string="Datetrx")
    total_sales_amt = fields.Float(string="Total Sales Amt")
    dis_amt = fields.Float(string="Discount Amt")
    round_off = fields.Float(string="RoundOff")
    tot_net_amt = fields.Float(string="Total Net Amt")
    bill_count = fields.Float(string="Bill Count")
    avg_bill = fields.Float(string="Avg Bill")
  
           
ss_total_sales_screen_line()
    
     
class ss_excel_extended_total_rep(models.Model):
    _name = "ss.excel.extended.total.rep"
    
    name = fields.Char(default="Download Excel Report")
    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64) 
    
    
