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

DATE_FORMAT_1 = "%d-%m-%y"
DATE_FORMAT_2 = "%d/%m/%y"
DATE_FORMAT_3 = "%d/%m/%y"

class pos_product_wise_sales_details_wzd(models.Model):
    _name = "ss.pos.product.exchange.report"
       
    start_date = fields.Date('Invoice From Date') 
    end_date = fields.Date('Invoice To Date') 

    cashier_id = fields.Many2one('cashier.master',string='Cashier')
    company_id = fields.Many2one('res.company',string='Company',default=lambda self:self.env.company.id)
    organization_id = fields.Many2one('organization.master', string="Organization")
    company_id_domain= fields.Char(
    compute="_compute_company_id_domain",
    readonly=True,
    store=False,
)


    @api.depends('company_id')
    def _compute_company_id_domain(self):
        if self.company_id:
            self.company_id_domain = json.dumps(
                [('org_id', '=',self.company_id.organization_id.org_id)]
            )
        
            
    def print_pos_report(self):

        def get_poslines(self):
            lis=[]
            start_date = self.start_date
            end_date = self.end_date
            cashier_id = self.cashier_id.name
            company_id = self.company_id.name
            organization_id=self.organization_id.name

            try:
                db_conn = self.env['db.connection'].search([('company_id','=',self.company_id.name)], limit=1)

                db_connect=db_conn.database_connect()

                cursor = db_connect.cursor()

                sqls='''
                      delete from ss_pos_exchange_product_screen_line
                       '''               
                self.env.cr.execute(sqls)
                    
                if cashier_id:
                    sql='''
                        select i.documentno as str_ExchangeBill,
                            (select string_agg(documentno::character varying,',') from c_invoice where 
                            c_invoice_id in (select c_invoice_id from c_invoice where c_order_id=o.ref_order_id)) as str_Originalbill,
                            i.dateinvoiced as dt_InvoiceDate,
                            p.value as str_productcode,
                            p.name as  str_productname,
                            il.qtyentered as return_qty,
                            il.priceactual as  NUM_OiginalInvoiceSP,
                            il.linenetamt as num_linetotal,
                            u.name as str_Cashier,
                            ps.name as str_Terminal
                            from c_invoiceline il
                            inner join c_invoice i on (i.c_invoice_id = il.c_invoice_id and il.UM_IsExchange='Y' and i.docstatus in ('CO','CL') and i.issotrx='Y')
                            inner join c_order o on (o.c_order_id = i.c_order_id and i.docstatus in ('CO','CL') and i.issotrx='Y')
                            inner join m_product p on (p.m_product_id = il.m_product_id)
                            inner join c_pos ps on (ps.c_pos_id = o.c_pos_id)
                            inner join ad_user u on (u.ad_user_id = i.createdby)
                            where i.dateinvoiced::date >= '%s' and i.dateinvoiced::date <='%s'
                            and(u.name='%s')
                            order by  i.documentno   
               
                          ''' %(start_date, end_date,cashier_id)
                    cursor.execute(sql)
                    
                else:
                    sql='''
                        select i.documentno as str_ExchangeBill,
                            (select string_agg(documentno::character varying,',') from c_invoice where 
                            c_invoice_id in (select c_invoice_id from c_invoice where c_order_id=o.ref_order_id)) as str_Originalbill,
                            i.dateinvoiced as dt_InvoiceDate,
                            p.value as str_productcode,
                            p.name as  str_productname,
                            il.qtyentered as return_qty,
                            il.priceactual as  NUM_OiginalInvoiceSP,
                            il.linenetamt as num_linetotal,
                            u.name as str_Cashier,
                            ps.name as str_Terminal
                            from c_invoiceline il
                            inner join c_invoice i on (i.c_invoice_id = il.c_invoice_id and il.UM_IsExchange='Y' and i.docstatus in ('CO','CL') and i.issotrx='Y')
                            inner join c_order o on (o.c_order_id = i.c_order_id and i.docstatus in ('CO','CL') and i.issotrx='Y')
                            inner join m_product p on (p.m_product_id = il.m_product_id)
                            inner join c_pos ps on (ps.c_pos_id = o.c_pos_id)
                            inner join ad_user u on (u.ad_user_id = i.createdby)
                            where i.dateinvoiced::date >= '%s' and i.dateinvoiced::date <='%s'
                            order by  i.documentno   
               
                          ''' %(start_date, end_date)
                    cursor.execute(sql)   
                                               
                pos_data = cursor.fetchall()

                for row in pos_data:                
                    dict = {'str_ExchangeBill':row[0],'str_Originalbill':row[1] ,'dt_InvoiceDate':row[2],
                            'str_productcode':row[3] ,'str_productname':row[4] ,
                            'return_qty':row[5] ,'NUM_OiginalInvoiceSP':row[6] ,
                            'num_linetotal':row[7], 'str_Cashier':row[8],'str_Terminal':row[9], }

                    lis.append(dict)

                return lis
            
            except (Exception, psycopg2.Error) as error:
                raise UserError(_("Error while fetching data from PostgreSQL "))
    
            finally: # closing database connection.
                if db_conn:
                    cursor.close()
                    db_connect.close()

            
    
        exc_qty = 0
        org_price = 0
        line_amnt = 0
        pos_order_line = []

        for line in get_poslines(self):
            exc_qty+=line['return_qty']
            org_price+=line['NUM_OiginalInvoiceSP']
            line_amnt+=line['num_linetotal']
     
            
            pos_order_line.append((0,0,{
                                'exchange_bill' : line['str_ExchangeBill'],
                                'original_bill' : line['str_Originalbill'],
                                'invoice_date' : line['dt_InvoiceDate'],
                                'product_code' : line['str_productcode'],
                                'product_name' : line['str_productname'],
                               
                                'return_qty' : line['return_qty'],
                                'original_invoicesp' : line['NUM_OiginalInvoiceSP'],
                                'line_total' : line['num_linetotal'],

                                'cashier' : line['str_Cashier'],
                                'terminal' : line['str_Terminal'],
                       
                                     }))
        if pos_order_line:
            pos_order_line.append((0,0,{  
                                'return_qty' : exc_qty,
                                'original_invoicesp' : org_price,
                                'line_total' : line_amnt,
                                     
                             }))    
#    
         
        vals = {
               'start_date' : self.start_date,
               'end_date' : self.end_date,
               'cashier_id' : self.cashier_id.name,
               'company_id' : self.company_id.name,

               'pos_order_line': pos_order_line,

                }
        ss_pos_wise_exchange_product_reports_id = self.env['ss.pos.product.screen.wzd'].create(vals)

        res = self.env['ir.model.data'].check_object_reference(
                                            'ss_pos_reports', 'ss_view_pos_order_wise_wzd_report')
        return {
                    'name': 'POS product wise exchange Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'ss.pos.product.screen.wzd',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': ss_pos_wise_exchange_product_reports_id.id,
            }
       
class pos_screen_wzd(models.Model):
    _name = "ss.pos.product.screen.wzd"
    _description = "Department Sales Orders Summary Reports"
    
    name = fields.Char(default = "POS product Exchange Report")
    pos_order_line = fields.One2many('ss.pos.exchange.product.screen.line','pos_id')
    start_date = fields.Date('Invoice From Date') 
    end_date = fields.Date('Invoice To Date') 
    company_id = fields.Char('Company')
    organization_id = fields.Char('Organization')
    cashier_id = fields.Char('Cashier')

        

    
    def print_pos_orders_excel_report(self):
        filename= 'POS Product Wise Exchange Report.xls'
        workbook= xlwt.Workbook(encoding="UTF-8")
        style_header = xlwt.easyxf('pattern: pattern solid, fore_colour light_orange;'
                               'font: bold on; font:height 230; align: wrap No; borders: left thin, right thin, top thin, bottom thin;')
        style = xlwt.easyxf('font:height 230; align: wrap No;borders: left thin, right thin, top thin, bottom thin;')
        header=xlwt.easyxf('pattern: pattern solid, fore_colour light_orange;''font:height 400; align: horiz center;font:bold True;' "borders: top thin,bottom thin , left thin, right thin")
        style = xlwt.easyxf('font:height 230; align: wrap No;')
        base_style = xlwt.easyxf('align: wrap yes')
        date_style = xlwt.easyxf('align: wrap yes', num_format_str='DD-MM-YYYY')
        datetime_style = xlwt.easyxf('align: wrap yes', num_format_str='DD-MM-YYYY HH:mm:SS')
        sheet= workbook.add_sheet('POS Product Wise Exchange Report')
        format6 = xlwt.easyxf('pattern: pattern solid, fore_colour light_yellow;''font:height 210,bold True;align: horiz left;'"borders: top thin,bottom thin , left thin, right thin")
        format1 = xlwt.easyxf('font: bold off, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color white;')
        

        start_date = self.start_date  or ''
        end_date = self.end_date  or ''
        cashier_id = self.cashier_id  or ''

        company_id = self.company_id or ''
        
        sheet.col(0).width = 700*8
        sheet.col(1).width = 700*8
        sheet.col(2).width = 700*8
        sheet.col(3).width = 700*8
        sheet.col(4).width = 850*8
        sheet.col(5).width = 700*8
        sheet.col(6).width = 700*8
        sheet.col(7).width = 700*8
        sheet.col(8).width = 700*8
        sheet.col(9).width = 700*8
        sheet.col(10).width = 700*8
        sheet.col(11).width = 700*8
        sheet.col(12).width = 700*8
        sheet.col(13).width = 700*8
        sheet.col(14).width = 850*8
        sheet.col(15).width = 850*8
        sheet.col(16).width = 850*8
        
        sheet.write(2, 0, 'Exchangebill', format6)
        sheet.write(2, 1, 'Originalbill', format6)
        sheet.write(2, 2, 'Invoicedate', format6)
        sheet.write(2, 3, 'Productcode', format6)
        sheet.write(2, 4, 'Productname', format6)
      
        sheet.write(2, 5, 'Exchangeqty', format6)
        sheet.write(2, 6, 'OriginalInvoicesp', format6)
        sheet.write(2, 7, 'Linetotal', format6)

        sheet.write(2, 8, 'Cashier', format6)
        sheet.write(2, 9, 'Terminal', format6)
      
        sheet.write_merge(0, 1, 0, 9, 'POS Product Exchange Report',header) 
 
               
        sql = '''
                 select exchange_bill,original_bill ,to_char(invoice_date,'dd/mm/yyyy'),product_code,
                 product_name,return_qty,original_invoicesp,line_total,cashier,terminal
                 
                 sales_rep from
                    ss_pos_exchange_product_screen_line         
                    where pos_id=(select max(pos_id) from ss_pos_exchange_product_screen_line)                        
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
        export_id = self.env['ss.excel.extended.pos.rep'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        
        fp.seek(0)
        data = fp.read()
        fp.close()

        return{
              'view_mode': 'form',
              'res_id': export_id.id,
              'res_model': 'ss.excel.extended.pos.rep',

              'type': 'ir.actions.act_window',
              'context': False,

          
            }
        
pos_screen_wzd()
 
class pos_product_screen_line(models.Model):
    _name = "ss.pos.exchange.product.screen.line"
    _description = "Sales summary Line"
    
    pos_id = fields.Many2one('ss.pos.product.screen.wzd',string='pos_id',ondelete='cascade')
    exchange_bill = fields.Char(string="Exchangebill")
    original_bill = fields.Char(string="Originalbill")
    invoice_date = fields.Date(string="Invoicedate")
    product_code = fields.Integer(string="Productcode")
    product_name = fields.Char(string="Productname")
    
    return_qty = fields.Float(string="Exchangeqty")
    original_invoicesp = fields.Char(string="Originalbillsp")
    line_total = fields.Float(string="Linetotal")

    cashier = fields.Char(string="Cashier")
    terminal = fields.Char(string="Terminal")
 
           
           
pos_product_screen_line()
    
     
class excel_extended_dept_open_orders_rep(models.Model):
    _name= "ss.excel.extended.pos.rep"
    
    name = fields.Char(default="Download Excel Report")
    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64) 
    
    