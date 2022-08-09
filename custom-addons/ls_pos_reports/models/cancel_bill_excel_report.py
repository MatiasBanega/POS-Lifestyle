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


DATE_FORMAT_1 = "%Y-%d-%m"
DATE_FORMAT_2 = "%d/%m/%y"
DATE_FORMAT_3 = "%m/%d/%y"


class itemwise_cancelled_bill_report_wzd(models.Model):
    _name = "itemwise.cancelled.report"
       
    start_date = fields.Date('Date From') 
    end_date = fields.Date(string="Date To") 
    company_id = fields.Many2one('res.company',string='Company',default=lambda self:self.env.company.id)

    
    def print_cancelled_report(self):
        
        
        def get_cancel_lines(self):
            res = {}
            dict={}
            lis=[]
            start_date = self.start_date
            end_date = self.end_date
            company_id = self.company_id.name
            try:
                db_conn = self.env['db.connection'].search([('company_id','=',self.company_id.name)], limit=1)
                #print('db_conn',db_conn.company_id,self.company_id)         
                db_connect=db_conn.database_connect()
                #print('function',db_connect)
                cursor = db_connect.cursor()
                self.env['bill.cancel.line'].search([]).unlink()
            
                sql='''
                       select i.dt_BillDate as dt_bdate,str_BillNo as str_bno,i.STR_UserName as STR_uname,
                        i.STR_productcode as STR_ptcode,
                        i.STR_productname as STR_ptname,
                        i.NUM_Totalamount as NUM_totamt from (
                        select i.dateinvoiced as dt_BillDate,
                       CASE WHEN og.um_isterminalwisedocsequence = 'N'::bpchar AND c.um_issuffix in ('N'::bpchar,'Y'::bpchar) THEN substr(i.documentno::text, 4)
                        WHEN c.um_issuffix = 'N'::bpchar THEN substr(i.documentno::text, 7) ELSE substr(i.documentno::text, 1, 6) END AS str_BillNo,
                        us.name as STR_UserName,
                        d.value as STR_productcode,
                        d.um_name as STR_productname,
                       CASE WHEN LAG(i.c_invoice_id) OVER (ORDER BY i.c_invoice_id, m.line) = i.c_invoice_id THEN NULL ELSE grandtotal END AS NUM_Totalamount
                       from c_invoice i
                       JOIN ad_orginfo og ON og.ad_org_id = i.ad_org_id
                        JOIN c_pos c ON c.c_pos_id = i.c_pos_id
                        JOIN ad_user us on us.ad_user_id=i.updatedby
                        join c_invoiceline m on m.c_invoice_id=i.c_invoice_id
                        join m_product d on d.m_product_id=m.m_product_id
                       WHERE i.issotrx = 'Y'::bpchar AND (i.docstatus = ANY (ARRAY['RE'::bpchar])) AND  i.c_invoice_id < i.reversal_id
                        AND (i.c_order_id > 0::numeric OR i.terminal IS NOT NULL)
                       union all
                           select i.dateinvoiced as dt_BillDate,
                        CASE WHEN og.um_isterminalwisedocsequence = 'N'::bpchar AND c.um_issuffix in ('N'::bpchar,'Y'::bpchar) THEN substr(i.documentno::text, 4)
                        WHEN c.um_issuffix = 'N'::bpchar THEN substr(i.documentno::text, 7) ELSE substr(i.documentno::text, 1, 6) END AS BillNo,
                        us.name as STR_UserName,
                        d.value as STR_productcode,
                        d.um_name as STR_productname,
                       grandtotal as NUM_Totalamount
                        from c_invoice i
                       JOIN ad_orginfo og ON og.ad_org_id = i.ad_org_id
                        JOIN c_pos c ON c.c_pos_id = i.c_pos_id
                        JOIN ad_user us on us.ad_user_id=i.updatedby
                        left join c_invoiceline m on m.c_invoice_id=i.c_invoice_id
                        left join m_product d on d.m_product_id=m.m_product_id
                        WHERE i.issotrx = 'Y'::bpchar AND (i.docstatus = ANY (ARRAY['DR'::bpchar,'IN'::bpchar,'IP'::bpchar]))
                        AND (i.c_order_id > 0::numeric OR i.terminal IS NOT NULL)
                        )i
                       where i.dt_BillDate::date  >= '%s' and i.dt_BillDate::date <='%s'
                      ''' %(start_date, end_date)
                    
                      
                cursor.execute(sql)
                #print(sql)
                cancel_data = cursor.fetchall()
                #print('cancel_data',cancel_data)
                for row in cancel_data:                
                    dict = {'dt_bdate':row[0],'str_bno':row[1] , 'STR_uname':row[2],'STR_ptcode':row[3] ,'STR_ptname':row[4] ,'NUM_totamt':row[5],}
                    #print('dictionary',dict)
                    lis.append(dict)
                #print('list',lis)
                return lis
            except (Exception, psycopg2.Error) as error:
                raise UserError(_("Error while fetching data from PostgreSQL "))
                #print("Error while fetching data from PostgreSQL", error)
    
            finally:
    # closing database connection.
                if db_conn:
                    cursor.close()
                    #print('db_connect',db_connect)
                    #print('close',db_connect.close)
                    db_connect.close()
                    #print('db_connect1',db_connect)
                    #print('close1',db_connect.close)
                    #print("PostgreSQL connection is closed")
                
                 
        tot_amt = 0

        
      
        cancel_order_line = []
        for line in get_cancel_lines(self):
            if line['NUM_totamt']:
                tot_amt+=line['NUM_totamt']

                         
            cancel_order_line.append((0,0,{
                                'bill_date' : line['dt_bdate'],
                                'bill_number' : line['str_bno'],
                                'uname' : line['STR_uname'],
                                'pcode' : line['STR_ptcode'],
                                'pname' : line['STR_ptname'],
                                'total_amt' : line['NUM_totamt'],
                                
                                     }))
        if cancel_order_line:
            cancel_order_line.append((0,0,{
                                    'pname' : 'Total',
                                    'total_amt' : tot_amt,
                                    
                                }))    
                            
         
        vals = {
               
                'start_date':self.start_date ,   
                'end_date':self.end_date ,  
                'company_id' : self.company_id.name,
                'cancel_order_line': cancel_order_line,
                           
                }
        cancel_bill_reports_id = self.env['item.wise.cancel.screen.wzd'].create(vals)

        res = self.env['ir.model.data'].check_object_reference(
                                            'ls_pos_reports', 'view_itemwise_cancelled_bill_report')
        return {
                    'name': 'Itemwise Cancel Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'item.wise.cancel.screen.wzd',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': cancel_bill_reports_id.id,
            }
    
    
    
    
    
    
    
    
class bill_screen_wizd_excel(models.Model):
    _name = "item.wise.cancel.screen.wzd"
    _description = "Cancelled Bill Summary Reports"
     
    name = fields.Char(string="Name", default="Cancelled Bill  Report")
    cancel_order_line = fields.One2many('bill.cancel.line','cancel_id',string='Open Order Line')
    start_date = fields.Date('Date From')
    end_date = fields.Date(string="Date To") 
    company_id = fields.Char(string="Company") 
 
     
    def print_cancel_bill_excel_report(self):
        filename= 'Itemwise Cancelled Bill Report.xls'
        workbook= xlwt.Workbook(encoding="UTF-8")
        
        style_header = xlwt.easyxf('pattern: pattern solid, fore_colour light_orange;'
                               'font: bold on; font:height 230; align: wrap No; borders: left thin, right thin, top thin, bottom thin;')
        style = xlwt.easyxf('font:height 230; align: wrap No;borders: left thin, right thin, top thin, bottom thin;')
        header=xlwt.easyxf('pattern: pattern solid, fore_colour light_orange;''font:height 400; align: horiz center;font:bold True;' "borders: top thin,bottom thin , left thin, right thin")
        style = xlwt.easyxf('font:height 230; align: wrap No;')
        base_style = xlwt.easyxf('align: wrap yes')
        date_style = xlwt.easyxf('align: wrap yes', num_format_str='DD-MM-YYYY')
        datetime_style = xlwt.easyxf('align: wrap yes', num_format_str='DD-MM-YYYY HH:mm:SS')
        sheet= workbook.add_sheet('Cancelled Bill Report Itemwise')
        format6 = xlwt.easyxf('pattern: pattern solid, fore_colour light_yellow;''font:height 210,bold True;align: horiz left;'"borders: top thin,bottom thin , left thin, right thin")
        format1 = xlwt.easyxf('font: bold off, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color white;')
        
        
        end_date = self.end_date  or ''
        start_date = self.start_date or ''
        company_id = self.company_id or ''

            
        sheet.col(0).width = 800*5
        sheet.col(1).width = 800*5
        sheet.col(2).width = 800*5
        sheet.col(3).width = 800*5
        sheet.col(4).width = 800*5
        sheet.col(5).width = 800*5
        sheet.col(6).width = 800*5
        sheet.col(7).width = 800*5 
        sheet.write(2, 0, 'Bill Date', format6)
        sheet.write(2, 1, 'Bill No', format6)
        sheet.write(2, 2, 'User Name', format6)
        sheet.write(2 ,3, 'Product Code', format6)
        sheet.write(2, 4, 'Product Name', format6)
        sheet.write(2, 5, 'Total Amount', format6)
        sheet.write_merge(0, 1, 0, 5, 'Cancelled Bill Report Itemwise',header)               
        sql = '''    
                   select bill_date,bill_number,uname,pcode,pname,total_amt from
                    bill_cancel_line         
                    where cancel_id=(select max(cancel_id) from bill_cancel_line)
                    
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
        export_id = self.env['excel.extended.itemwise.cancel.rpt'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        
        fp.seek(0)
        data = fp.read()
        fp.close()

        return{
              'view_mode': 'form',
              'res_id': export_id.id,
              'res_model': 'excel.extended.itemwise.cancel.rpt',
              'type': 'ir.actions.act_window',
              'context': False,
                     
            }
        
bill_screen_wizd_excel()
     
    
    
class cancelled_bill_screen_line(models.Model):
    _name = "bill.cancel.line"
    _description = "Itemwise Cancelled"
    
    cancel_id = fields.Many2one('item.wise.cancel.screen.wzd',string='cancel_id',ondelete='cascade')
    date = fields.Date(string="Date")
    bill_date = fields.Date(string="Bill Date")
    bill_number = fields.Integer(string="Bill No")
    uname = fields.Char(string="User Name")
    pcode = fields.Integer(string="Product Code")
    pname = fields.Char(string="Product Name")
    total_amt = fields.Float(string="Total Amount")
    
           
cancelled_bill_screen_line()    


class excel_extended_itemwise_cancel_bill_rpt(models.Model):
    _name= "excel.extended.itemwise.cancel.rpt"
    
    name = fields.Char(default="Itemwise Cancelled Report")
    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64) 
    
    