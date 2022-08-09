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

class bill_count_report_wzd(models.Model):
    _name = "billcount.report"
       
    start_date = fields.Date('Date From') 
    end_date = fields.Date(string="Date To") 
    company_id = fields.Many2one('res.company',string='Company',default=lambda self:self.env.company.id)
   
    def print_billcount_report(self):

        def get_lines(self):
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
                self.env['billno.count.line'].search([]).unlink()
                sql='''
                     select b.terminal as terminal,
                    b.STR_startno as startno,
                    b.STR_endno as endno, 
                    (b.INT_totalbillcount+b.INT_cancelcount+b.INT_draftcount) as INT_totalbillcount,
                    (b.INT_onlinecnt+b.INT_cancelcount+b.INT_draftcount) as  INT_onlinecount, 
                    b.INT_offlinecnt as INT_offlinecount, 
                    (b.INT_cancelcount+b.INT_draftcount) as INT_cancelcount 
                    
                    from (
                    with invoice as
                    (select c.c_invoice_id,c.c_doctype_id,c.c_doctypetarget_id,c.dateinvoiced,c.docstatus,c.c_pos_id
                      FROM c_invoice c
                    where c.dateinvoiced::date >= '%s' and c.dateinvoiced::date <='%s' 
                      )
                      
                     SELECT 'B2C' as terminal,
                     sum(( select count(1) from c_invoice where c_invoice_id=c.c_invoice_id 
                     and (docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar])) and c.c_doctype_id in
                     (select c_doctype_id from c_doctype Where name in('AR Invoice Indirect','AR Invoice'))
                     ) ) AS INT_totalbillcount,
                     
                       round(sum(( select count(1) from c_invoice where c_invoice_id=c.c_invoice_id 
                     and (docstatus = ANY (ARRAY['RE'::bpchar, 'VO'::bpchar])) and c.c_doctype_id in
                     (select c_doctype_id from c_doctype Where name in('AR Invoice Indirect','AR Invoice'))
                     ))/2,0) AS INT_cancelcount,
                     
                    min((select substr(documentno,4)::numeric from c_invoice 
                     where  c_invoice_id=c.c_invoice_id
                     and (documentno not like '%%O%%' and documentno not like '3%%' and documentno not like '2%%' and documentno not like '%%^')
                     and c.c_doctypetarget_id in
                     (select c_doctype_id from c_doctype Where name in('AR Invoice Indirect','AR Invoice'))
                     )) AS STR_startno, 
                     
                    max((select substr(documentno,4)::numeric from c_invoice 
                    where c_invoice_id=c.c_invoice_id 
                      and (documentno not like '%%O%%' and documentno not like '3%%' and documentno not like '2%%' and documentno not like '%%^')
                      and c.c_doctype_id in
                     (select c_doctype_id from c_doctype Where name in('AR Invoice Indirect','AR Invoice')) 
                     )) AS STR_endno,
                     
                     sum((select count(1) from c_invoice where c_invoice_id=c.c_invoice_id  
                     AND (c.docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar])) and documentno not like '%%O%%' and c.c_doctype_id in
                     (select c_doctype_id from c_doctype Where name in('AR Invoice Indirect','AR Invoice')) 
                     )) as INT_onlinecnt,
                     
                     sum((select count(1) from c_invoice where c_invoice_id=c.c_invoice_id 
                     AND (c.docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar])) and (documentno like '3%%' or documentno like '2%%') 
                     and c.c_doctype_id in
                      (select c_doctype_id from c_doctype Where name in('AR Invoice Indirect','AR Invoice')) 
                     )) as INT_offlinecnt, 
                     
                     sum(( select count(1) from c_invoice where c_invoice_id=c.c_invoice_id 
                     and (docstatus = ANY (ARRAY['DR'::bpchar, 'IP'::bpchar, 'IN'::bpchar])) and c.c_doctypetarget_id in
                       (select c_doctype_id from c_doctype Where name in('AR Invoice Indirect','AR Invoice')) 
                     )) AS INT_draftcount
                     
                       FROM invoice c
                       
                     union all
                     
                     SELECT 'B2B' as terminal,
                     sum(( select count(1) from c_invoice where c_invoice_id=c.c_invoice_id 
                     and (docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar])) and c.c_doctype_id in
                     (select c_doctype_id from c_doctype Where name in('AR Invoice Indirect - GST','AR Invoice - GST'))
                     ) ) AS INT_totalbillcount,
                     
                       round(sum(( select count(1) from c_invoice where c_invoice_id=c.c_invoice_id 
                     and (docstatus = ANY (ARRAY['RE'::bpchar, 'VO'::bpchar])) and c.c_doctype_id in
                     (select c_doctype_id from c_doctype Where name in('AR Invoice Indirect - GST','AR Invoice - GST'))
                     ))/2,0) AS INT_cancelcount,
                     
                    min((select substr(documentno,4)::numeric from c_invoice 
                     where  c_invoice_id=c.c_invoice_id
                     and (documentno not like '%%O%%' and documentno not like '3%%' and documentno not like '2%%' and documentno not like '%%^')
                     and c.c_doctypetarget_id in
                     (select c_doctype_id from c_doctype Where name in('AR Invoice Indirect - GST','AR Invoice - GST'))
                     )) AS STR_startno,
                     
                    max((select substr(documentno,4)::numeric from c_invoice 
                    where c_invoice_id=c.c_invoice_id
                      and (documentno not like '%%O%%' and documentno not like '3%%' and documentno not like '2%%' and documentno not like '%%^')
                      and c.c_doctype_id in
                     (select c_doctype_id from c_doctype Where name in('AR Invoice Indirect - GST','AR Invoice - GST')) 
                     )) AS STR_endno,
                     
                     sum((select count(1) from c_invoice where c_invoice_id=c.c_invoice_id  
                     AND (c.docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar])) and documentno not like '%%O%%' and c.c_doctype_id in
                     (select c_doctype_id from c_doctype Where name in('AR Invoice Indirect - GST','AR Invoice - GST')) 
                     )) as INT_onlinecnt,
                     
                     sum((select count(1) from c_invoice where c_invoice_id=c.c_invoice_id 
                     AND (c.docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar])) and (documentno like '3%%' or documentno like '2%%') 
                     and c.c_doctype_id in
                      (select c_doctype_id from c_doctype Where name in('AR Invoice Indirect - GST','AR Invoice - GST')) 
                     )) as INT_offlinecnt, 
                     
                     sum(( select count(1) from c_invoice where c_invoice_id=c.c_invoice_id 
                     and (docstatus = ANY (ARRAY['DR'::bpchar, 'IP'::bpchar, 'IN'::bpchar])) and c.c_doctypetarget_id in
                       (select c_doctype_id from c_doctype Where name in('AR Invoice Indirect - GST','AR Invoice - GST')) 
                     )) AS INT_draftcount
                     
                       FROM invoice c
                       
                    )b
                    Where b.int_totalbillcount>0
                     '''  %(start_date, end_date)
                        
                        
                cursor.execute(sql)
                #print(sql)
                billno_data = cursor.fetchall()
                #print('billno_data',billno_data)
                for row in billno_data:                
                    dict = {'terminal':row[0],'startno':row[1] , 'endno':row[2],'INT_totalbillcount':row[3] ,'INT_onlinecount':row[4] ,'INT_offlinecount':row[5] ,'INT_cancelcount':row[6] ,}
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
        bill_cnt = 0
        online_cnt = 0
        offline_cnt = 0
        cancel_cnt = 0
        draft_cnt = 0
      
        billno_count_line = []
   
        for line in get_lines(self):

            bill_cnt+=line['INT_totalbillcount']
            online_cnt+=line['INT_onlinecount']
            offline_cnt+=line['INT_offlinecount']
            cancel_cnt+=line['INT_cancelcount']
         
#             if line['delivered_qty']:
#                 dlry_qty+=line['delivered_qty']
#                          
            billno_count_line.append((0,0,{
                                'terminal' : line['terminal'],
                                'startno' : line['startno'],
                                'endno' : line['endno'],
                                'totalbillcount' : line['INT_totalbillcount'],
                                'onlinecnt' : line['INT_onlinecount'],
                                'oflinecnt' : line['INT_offlinecount'],
                                'cancelcount' : line['INT_cancelcount'],
                           
                                
                                     }))
        if billno_count_line:
            billno_count_line.append((0,0,{
                                    'terminal' : 'Total',
                                    'totalbillcount' : bill_cnt,
                                    'onlinecnt' :online_cnt, 
                                    'oflinecnt' : offline_cnt,
                                    'cancelcount' : cancel_cnt,
                                }))    
                            
         
        vals = {
                #'name': 'Beat outstanding Report',
                'start_date':self.start_date ,   
                'end_date':self.end_date ,             
                'company_id':self.company_id.name, 
#                  'customer_type_title':'TYPE: ',             
#                  'customer_type': self.customer_type,
                'billno_count_line': billno_count_line,
                #'visible':True,            
                }
        bill_count_reports_id = self.env['bill.count.report.wzd'].create(vals)

        res = self.env['ir.model.data'].check_object_reference(
                                            'ls_pos_reports', 'view_bill_count_report')
        return {
                    'name': 'Bill No Count Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'bill.count.report.wzd',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': bill_count_reports_id.id,
            }
       
class billcount_screen_wzd(models.Model):
    _name = "bill.count.report.wzd"
    _description = "Bill No Count Reports"
    
    name=fields.Char(string="Name",default='Bill No Count Report')
    billno_count_line = fields.One2many('billno.count.line','bill_id',string='Bill Count Line')
    start_date = fields.Date('Date From') #, required=True
    end_date = fields.Date(string="Date To")
    company_id = fields.Char(string='Company')
                  
    def print_bill_count_excel_report(self):
        filename= 'Bill No Count Report.xls'
        workbook= xlwt.Workbook(encoding="UTF-8")
        style_header = xlwt.easyxf('pattern: pattern solid, fore_colour light_orange;'
                               'font: bold on; font:height 230; align: wrap No; borders: left thin, right thin, top thin, bottom thin;')
        style = xlwt.easyxf('font:height 230; align: wrap No;borders: left thin, right thin, top thin, bottom thin;')
        header=xlwt.easyxf('pattern: pattern solid, fore_colour light_orange;''font:height 400; align: horiz center;font:bold True;' "borders: top thin,bottom thin , left thin, right thin")
        style = xlwt.easyxf('font:height 230; align: wrap No;')
        base_style = xlwt.easyxf('align: wrap yes')
        date_style = xlwt.easyxf('align: wrap yes', num_format_str='DD-MM-YYYY')
        datetime_style = xlwt.easyxf('align: wrap yes', num_format_str='DD-MM-YYYY HH:mm:SS')
        sheet= workbook.add_sheet('Bill No Count Report')
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
        sheet.write(2, 0, 'Terminal', format6)
        sheet.write(2, 1, 'Startno', format6)
        sheet.write(2, 2, 'Endno', format6)
        sheet.write(2 ,3, 'Total Bill Count', format6)
        sheet.write(2, 4, 'Online Count', format6)
        sheet.write(2, 5, 'Offline Count', format6)
        sheet.write(2, 6, 'Cancel Count', format6)
        sheet.write_merge(0, 1, 0, 6, 'Bill No Count Report',header)               
        sql = '''    
                   select terminal,startno ,endno,totalbillcount,oflinecnt,onlinecnt,cancelcount from
                    billno_count_line         
                    where bill_id=(select max(bill_id) from billno_count_line)   
                    
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
        export_id = self.env['excel.extended.billcount.rep'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        
        fp.seek(0)
        data = fp.read()
        fp.close()

        return{
              'view_mode': 'form',
              'res_id': export_id.id,
              'res_model': 'excel.extended.billcount.rep',
              #'view_type': 'form',
              'type': 'ir.actions.act_window',
              'context': False,
              #'target': 'new',
          
            }
        
billcount_screen_wzd()
 
class billno_count_screen_line(models.Model):
    _name = "billno.count.line"
    _description = "Bill Count"
    
    bill_id = fields.Many2one('bill.count.report.wzd',string='bill_id',ondelete='cascade')
    terminal = fields.Char(string="Terminal")
    startno = fields.Integer(string="Startno")
    endno = fields.Integer(string="Endno")
    totalbillcount = fields.Integer("Total Bill Count")
    oflinecnt = fields.Integer(string="Offline Count")
    onlinecnt = fields.Integer(string="Online Count")
    cancelcount = fields.Integer(string="Cancel Count")
   
    
           
billno_count_screen_line()
    
     
class excel_extended_billno_count_rep(models.Model):
    _name= "excel.extended.billcount.rep"
    
    name=fields.Char(string="Name",default='Download Excel Report')
    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64) 
    
    
