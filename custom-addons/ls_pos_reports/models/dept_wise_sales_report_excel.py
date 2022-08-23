from datetime import datetime
from odoo.exceptions import UserError
from datetime import date 
from dateutil.relativedelta import relativedelta
from odoo.osv import osv
from odoo import api, fields, models
from odoo import exceptions, _
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

class department_wise_sales_details_wzd(models.Model):
    _name = "dept.wise.sales.report"
       
    start_date = fields.Date('Date From') 
    end_date = fields.Date('Date To')
    company_id = fields.Many2one('res.company',string='Company',default=lambda self:self.env.company.id)
     
    def print_dept_report(self):
        
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
                self.env['dept.wise.sales.line'].search([]).unlink()
                
                sql='''
                select department ,  
                            (x.TotalAmt-(COALESCE(x.um_cgst,0)+COALESCE(x.um_sgst,0)+COALESCE(x.um_cessamt,0)))as NUM_TaxableAmt,
                            COALESCE(x.um_cgst,0)+COALESCE(x.um_sgst,0) as NUM_taxamt,
                            COALESCE(x.um_cgst,0) as NUM_cgst,COALESCE(x.um_sgst,0) as NUM_sgst,COALESCE(x.um_cessamt,0) as NUM_cessAmt,
                            x.num_markdown as NUM_MarkDown,
                            x.TotalAmt as NUM_TotalAmt
                            from (
                            SELECT pd.name as department,
                            ROUND(SUM(il.linenetamt), 4) AS TotalAmt,
                            ROUND(SUM(il.qtyinvoiced * il.priceentered / (100::NUMERIC + c.rate +
                            CASE WHEN il.um_cesstax_id > 0::NUMERIC
                                 THEN cesst.rate
                                 ELSE 0::NUMERIC
                             END) * c.um_cgst_rate ), 4) AS um_cgst,
                            ROUND(SUM(il.qtyinvoiced * il.priceentered / (100::NUMERIC + c.rate +
                            CASE
                              WHEN il.um_cesstax_id > 0::NUMERIC
                              THEN cesst.rate
                              ELSE 0::NUMERIC
                            END) * c.um_sgst_rate ), 4) AS um_sgst,
                            ROUND(SUM(il.qtyinvoiced * il.priceentered / (100::NUMERIC + c.rate +
                              CASE
                              WHEN il.um_cesstax_id > 0::NUMERIC
                              THEN cesst.rate
                              ELSE 0::NUMERIC
                            END) *
                             CASE
                             WHEN il.um_cesstax_id > 0::NUMERIC
                             THEN cesst.rate
                             ELSE 0::NUMERIC
                             END), 2)      AS um_cessamt,
                             ROUND(SUM(p.um_markdown),4) AS num_markdown
                            FROM c_invoiceline il
                            JOIN m_product p    ON p.m_product_id = il.m_product_id
                            inner join UM_Product_Department pd on (pd.UM_Product_Department_ID=p.UM_Product_Department_ID)
                            JOIN c_invoice i    ON i.c_invoice_id = il.c_invoice_id
                            JOIN c_tax c    ON c.c_tax_id = il.c_tax_id
                            LEFT JOIN c_tax cesst    ON cesst.c_tax_id = il.um_cesstax_id
                            WHERE i.issotrx   = 'Y'::bpchar
                            AND (i.docstatus  = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar]))
                            AND (i.c_order_id > 0::NUMERIC
                            OR i.terminal    IS NOT NULL)
                            AND  i.dateinvoiced::date >= '%s' and  i.dateinvoiced::date <='%s'
                            GROUP BY pd.name
                            ORDER BY department
                            )x
                      ''' %(start_date, end_date)

                cursor.execute(sql)
                sale_data = cursor.fetchall()
                for row in sale_data:                
                    dict = {'department':row[0],'NUM_TaxableAmt':row[1] , 'NUM_taxamt':row[2],'NUM_cgst':row[3] ,'NUM_sgst':row[4] ,'NUM_cessAmt':row[5] ,'NUM_MarkDown':row[6] ,'NUM_TotalAmt':row[7] ,}
                  
                    lis.append(dict)
                return lis
            except (Exception, psycopg2.Error) as error:
                raise UserError(_("Error while fetching data from PostgreSQL "))

            finally:
    # closing database connection.
                if db_conn:
                    cursor.close()
                    db_connect.close()
                    
        
        tot_tax = 0
        tot_tax_amt = 0
        tot_cgst = 0
        tot_sgst = 0
        tot_cessamt = 0
        tot_mark_down = 0
        tot_total = 0
        dept_wise_sale_line = []
        
        for line in get_lines(self):
            if line['NUM_TaxableAmt']:
                tot_tax+=line['NUM_TaxableAmt']
            if line['NUM_taxamt']:
                tot_tax_amt+=line['NUM_taxamt']
            if line['NUM_cgst']:
                tot_cgst+=line['NUM_cgst']
            if line['NUM_sgst']:
                tot_sgst+=line['NUM_sgst']
            if line['NUM_cessAmt']:
                tot_cessamt+=line['NUM_cessAmt']
            if line['NUM_MarkDown']:
                tot_mark_down+=line['NUM_MarkDown']
            if line['NUM_TotalAmt']:
                tot_total+=line['NUM_TotalAmt']
                         
            dept_wise_sale_line.append((0,0,{
                                'department' : line['department'],
                                'tax' : line['NUM_TaxableAmt'],
                                'tax_amt' : line['NUM_taxamt'],
                                'cgst' : line['NUM_cgst'],  
                                'sgst' : line['NUM_sgst'],
                                'cessamt' : line['NUM_cessAmt'],
                                'mark_down' : line['NUM_MarkDown'],
                                'total' : line['NUM_TotalAmt'],  
                                
                                     }))
        if dept_wise_sale_line:
            dept_wise_sale_line.append((0,0,{  
                                'tax' : tot_tax,
                                'tax_amt' : tot_tax_amt,
                                'cgst' : tot_cgst,
                                'sgst' : tot_sgst,
                                'cessamt' : tot_cessamt,
                                'mark_down' : tot_mark_down,
                                'total' : tot_total
                            }))    
   
         
        vals = {
               'start_date' : self.start_date,
               'end_date' : self.end_date,
               'company_id': self.company_id.name,

                'dept_wise_sale_line': dept_wise_sale_line,

                }
        dept_reports_id = self.env['dept.screen.wzd'].create(vals)

        res = self.env['ir.model.data'].check_object_reference(
                                            'ls_pos_reports', 'view_dept_wise_sale_screen_wzd_report')
        return {
                    'name': 'dept wise sales Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'dept.screen.wzd',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': dept_reports_id.id,
            }
       
class dept_sale_screen_wzd(models.Model):
    _name = "dept.screen.wzd"
    _description = "Department Wise Sales Reports"
    
    name = fields.Char(default="Dept Wise Sales Report")
    dept_wise_sale_line = fields.One2many('dept.wise.sales.line','deptsale_id')
    start_date = fields.Date('Date From')
    end_date = fields.Date('Date To')
    company_id = fields.Char('Company')

    
    def print_dept_orders_excel_report(self):
        filename= 'Department Wise Sales Report.xls'
        
        workbook= xlwt.Workbook(encoding="UTF-8")
        style_header = xlwt.easyxf('pattern: pattern solid, fore_colour light_orange;'
                               'font: bold on; font:height 230; align: wrap No; borders: left thin, right thin, top thin, bottom thin;')
        style = xlwt.easyxf('font:height 230; align: wrap No;borders: left thin, right thin, top thin, bottom thin;')
        header=xlwt.easyxf('pattern: pattern solid, fore_colour light_orange;''font:height 400; align: horiz center;font:bold True;' "borders: top thin,bottom thin , left thin, right thin")
        style = xlwt.easyxf('font:height 230; align: wrap No;')
        base_style = xlwt.easyxf('align: wrap yes')
        date_style = xlwt.easyxf('align: wrap yes', num_format_str='DD-MM-YYYY')
        datetime_style = xlwt.easyxf('align: wrap yes', num_format_str='DD-MM-YYYY HH:mm:SS')
        sheet= workbook.add_sheet('Terminal Wise Sales Report')
        format6 = xlwt.easyxf('pattern: pattern solid, fore_colour light_yellow;''font:height 210,bold True;align: horiz left;'"borders: top thin,bottom thin , left thin, right thin")
        format7 = xlwt.easyxf("borders: top thin,bottom thin , left thin, right thin")
       
        format1 = xlwt.easyxf('font: bold off, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color white;')
        end_date = self.end_date  or ''
        start_date = self.start_date or ''
        company_id = self.company_id or ''
        
            
        sheet.col(0).width = 850*5 
        sheet.col(1).width = 850*5
        sheet.col(2).width = 850*5
        sheet.col(3).width = 850*5    
        sheet.col(4).width = 850*5 
        sheet.col(5).width = 850*5
        sheet.col(6).width = 850*5
        sheet.col(7).width = 850*5  
        sheet.write(2, 0, 'Department', format6)
        sheet.write(2, 1, 'Taxable Amt', format6)
        sheet.write(2, 2, 'Tax Amt', format6)
        sheet.write(2 ,3, 'Cgst', format6)
        sheet.write(2, 4, 'Sgst', format6)
        sheet.write(2, 5, 'Cessamt', format6)
        sheet.write(2, 6, 'Markdown', format6)
        sheet.write(2 ,7, 'Total Amt', format6)
        sheet.write_merge(0, 1, 0, 3, 'Dept Wise Sales Report',header)

           
               
        sql = '''
                 select department,tax ,tax_amt,cgst,sgst,cessamt,mark_down,total from
                    dept_wise_sales_line         
                    where deptsale_id=(select max(deptsale_id) from dept_wise_sales_line)                        
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
        export_id = self.env['excel.extended.dept.rep'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        
        fp.seek(0)
        data = fp.read()
        fp.close()

        return{
              'view_mode': 'form',
              'res_id': export_id.id,
              'res_model': 'excel.extended.dept.rep',

              'type': 'ir.actions.act_window',
              'context': False,
          
            }
        
dept_sale_screen_wzd()
 
class dept_wise_sale_screen_line(models.Model):
    _name = "dept.wise.sales.line"
    _description = "Sales summary Line"
    
    deptsale_id = fields.Many2one('dept.screen.wzd',string='deptsale_id',ondelete='cascade')
    department = fields.Char(string="Department")
    tax = fields.Float(string="Taxable Amt")
    tax_amt = fields.Float(string="Tax Amt")
    cgst = fields.Float(string="Cgst")
    sgst = fields.Float(string="Sgst")
    cessamt = fields.Float(string="Cessamt")
    mark_down = fields.Float(string="Markdown")
    total = fields.Float(string="Total Amt")
  
           
dept_wise_sale_screen_line()
    
     
class excel_extended_orders_rep(models.Model):
    _name= "excel.extended.dept.rep"
    
    name = fields.Char(default="Download XLS Report")
    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64) 
    
    
