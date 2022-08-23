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

DATE_FORMAT_1 = "%d-%m-%y"
DATE_FORMAT_2 = "%m/%d/%y"
DATE_FORMAT_3 = "%y/%m/%d"

class ss_inter_branch_transfer_wzd(models.Model):
    _name = "ss.inter.branch.transfer.report"
       
    start_date = fields.Date() 
    end_date = fields.Date()
    company = fields.Many2one('res.company',string='Company',default=lambda self:self.env.company.id)
      
    def print_ss_inter_branch(self):

        def get_branch_lines(self):
            dict = {}
            lis = []
            start_date = self.start_date
            end_date = self.end_date
            company = self.company.name
            try:
                db_conn = self.env['db.connection'].search([('company_id','=',self.company.name)], limit=1)

                db_connect=db_conn.database_connect()

                cursor = db_connect.cursor() 
                self.env['ss.inter.branch.transfer.screen.line'].search([]).unlink()
                sql='''
                       
select o.value as STR_Branch, b.name as Inter_Branch,
i.description as STR_Description,i.documentno as STR_doc_no,
i.movementdate,p.value as STR_Code,p.name as STR_Product_Name,
abs(round((il.qtycount-il.qtybook),2)) as NUM_transfer_qty,round(il.um_mrp,2) as NUM_Mrp,
round(il.um_basiccost,2) as NUM_basiccost,
abs(round((il.um_basiccost*(il.qtycount-il.qtybook)),2)) as NUM_basiccost_total,
t.name as STR_tax,
abs(round(il.um_netcost,2)) as NUM_L_Cost,
abs(round(il.um_netlandcost, 2)) AS NUM_LCost_Total ,
dp.name as STR_Department,pc.name as STR_Category,ps.name as STR_Sub_Category,
cb.name as STR_Vendor,dc.printname as STR_Doc_Type
from m_inventory i 
join m_inventoryline il on i.m_inventory_id=il.m_inventory_id
left join UM_branch b on b.UM_branch_ID = i.UM_branch_ID
JOIN c_doctype dc on dc.c_doctype_id=i.c_doctype_id
join m_product p on p.m_product_id=il.m_product_id
join ad_org o on o.ad_org_id=i.ad_org_id
JOIN M_Product_Category pc ON pc.M_Product_Category_ID = il.M_Product_Category_ID
LEFT JOIN UM_Product_SubCategory ps ON ps.UM_Product_SubCategory_ID = p.UM_Product_SubCategory_ID
JOIN um_product_department dp ON dp.um_product_department_id = il.um_product_department_id 
left JOIN um_subdoctype su on su.um_subdoctype_id=il.um_subdoctype_id
LEFT JOIN m_product_po mp ON mp.m_product_id = p.m_product_id AND mp.iscurrentvendor = 'Y'::bpchar
LEFT JOIN c_bpartner cb on cb.c_bpartner_id = mp.c_bpartner_id
left join c_taxcategory t on t.c_taxcategory_id=il.um_purchasetaxcategory_id
where i.c_doctype_id in (select c_doctype_id from c_doctype where name in 
('Inter Branch Transfer Receive','Inter Branch Transfer Send'))
and (i.docstatus in ('CO','CL')) and i.movementdate::date >= '%s' and i.movementdate::date <= '%s'
                        order by i.movementdate  
                      '''%(start_date, end_date)
                             
                cursor.execute(sql)
                sale_data = cursor.fetchall()
                for row in sale_data:                
                    dict = {'STR_Branch':row[0],'Inter_Branch':row[1] , 'STR_Description':row[2],'STR_doc_no':row[3] ,
                            'movement_date':row[4],'STR_Code':row[5],'STR_Product_Name':row[6],'NUM_transfer_qty':row[7],
                            'NUM_Mrp':row[8],'NUM_basiccost':row[9],'NUM_basiccost_total':row[10],
                            'STR_tax':row[11],'NUM_L_Cost':row[12],
                            'NUM_LCost_Total':row[13],'STR_Department':row[14] , 'STR_Category':row[15],'STR_Sub_Category':row[16] ,
                            'STR_Vendor':row[17],'STR_Doc_Type':row[18],}
                        
                    lis.append(dict)
                return lis            
            except (Exception, psycopg2.Error) as error:
                raise UserError(_("Error while fetching data from PostgreSQL "))

            finally:
    # closing database connection.
                if db_conn:
                    cursor.close()
                    db_connect.close()
                    
        ss_inter_branch_line = []
        transfer_qty_tot = 0
        mrp_tot = 0
        basic_cost_tot = 0
        basic_cost_total_tot = 0
        l_cost_tot = 0
        l_cost_total_tot = 0
        for line in get_branch_lines(self):
            if line['NUM_transfer_qty']:
                transfer_qty_tot+=line['NUM_transfer_qty']
            if line['NUM_Mrp']:
                mrp_tot+=line['NUM_Mrp']
            if line['NUM_basiccost']:
                basic_cost_tot+=line['NUM_basiccost']
            if line['NUM_basiccost_total']:
                basic_cost_total_tot+=line['NUM_basiccost_total']
            if line['NUM_L_Cost']:
                l_cost_tot+=line['NUM_L_Cost']
            if line['NUM_LCost_Total']:
                l_cost_total_tot+=line['NUM_LCost_Total']             
            ss_inter_branch_line.append((0,0,{
                                'branch' : line['STR_Branch'],
                                'inter_branch' : line['Inter_Branch'],
                                'description' : line['STR_Description'],
                                'doc_no' : line['STR_doc_no'],
                                'movement_date' : line['movement_date'],
                                'code' : line['STR_Code'],
                                'product_name' : line['STR_Product_Name'],
                                
                                'transfer_qty' : line['NUM_transfer_qty'],
                                'mrp' : line['NUM_Mrp'],
                                'basic_cost' : line['NUM_basiccost'],
                                'basic_cost_total' : line['NUM_basiccost_total'],
                                'tax' : line['STR_tax'],
                                'l_cost' : line['NUM_L_Cost'],
                                'l_cost_total' : line['NUM_LCost_Total'],
                                'department' : line['STR_Department'],
                                'category' : line['STR_Category'],
                                'sub_category' : line['STR_Sub_Category'],
                                'vendor' : line['STR_Vendor'],
                                'doc_type' : line['STR_Doc_Type'],
                                     }))
        if ss_inter_branch_line:
            ss_inter_branch_line.append((0,0,{  
                                'transfer_qty' : transfer_qty_tot,
                                'mrp' : mrp_tot,
                                'basic_cost' : basic_cost_tot,
                                'basic_cost_total' : basic_cost_total_tot,
                                'l_cost' : l_cost_tot,
                                'l_cost_total' : l_cost_total_tot,
                                
                            }))
         
        vals = {
               'start_date' : self.start_date,
               'end_date': self.end_date,
               'company': self.company.name,
               'ss_inter_branch_line': ss_inter_branch_line,
                }
        inter_branch_transfer_report_id = self.env['ss.inter.branch.transfer.screen.wzd'].create(vals)

        res = self.env['ir.model.data'].check_object_reference(
                                            'ss_pos_reports', 'view_ss_inter_branch_transfer_wzd_report')
        return {
                    'name': 'department Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'ss.inter.branch.transfer.screen.wzd',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': inter_branch_transfer_report_id.id,
            }
       
class ss_inter_branch_screen_wzd(models.Model):
    _name = "ss.inter.branch.transfer.screen.wzd"
    _description = "Department Sales Orders Summary Reports"
    
    name = fields.Char(default="Inter Branch Transfer Report")
    ss_inter_branch_line = fields.One2many('ss.inter.branch.transfer.screen.line','ss_inter_branch_id',string='Open Order Line')
    start_date = fields.Date('Date From')
    end_date = fields.Date("Date TO")
    company = fields.Char(string="Company")

    def print_ss_inter_branch_excel_report(self):
        filename= 'Inter Branch Transfer Report.xls'
        workbook= xlwt.Workbook(encoding="UTF-8")
        
        
        style_header = xlwt.easyxf('pattern: pattern solid, fore_colour light_orange;'
                               'font: bold on; font:height 230; align: wrap No; borders: left thin, right thin, top thin, bottom thin;')
        style = xlwt.easyxf('font:height 230; align: wrap No;borders: left thin, right thin, top thin, bottom thin;')
        header=xlwt.easyxf('pattern: pattern solid, fore_colour light_orange;''font:height 400; align: horiz center;font:bold True;' "borders: top thin,bottom thin , left thin, right thin")
        style = xlwt.easyxf('font:height 230; align: wrap No;')
        base_style = xlwt.easyxf('align: wrap yes')
        date_style = xlwt.easyxf('align: wrap yes', num_format_str='DD-MM-YYYY')
        datetime_style = xlwt.easyxf('align: wrap yes', num_format_str='DD-MM-YYYY HH:mm:SS')
        sheet= workbook.add_sheet('Inter Branch Transfer Report')
        format6 = xlwt.easyxf('pattern: pattern solid, fore_colour light_yellow;''font:height 280,bold True;align: horiz left;'"borders: top thin,bottom thin , left thin, right thin")
        format7 = xlwt.easyxf('pattern: pattern solid, fore_colour light_yellow;''font:height 280,bold True;align: horiz center;'"borders: top thin,bottom thin , left thin, right thin")
        format1 = xlwt.easyxf('font: bold off, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color white;')

        start_date = self.start_date  or ''
        end_date = self.end_date  or ''
            
        sheet.col(0).width = 850*8
        sheet.col(1).width = 850*8
        sheet.col(2).width = 850*8
        sheet.col(3).width = 850*8
        sheet.col(4).width = 850*8
        sheet.col(5).width = 850*8
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
        sheet.write(2, 0, 'Branch', format6)
        sheet.write(2, 1, 'Inter Branch', format6)
        sheet.write(2, 2, 'Description', format6)
        sheet.write(2, 3, 'Doc No', format6)
        sheet.write(2, 4, 'Movement Date', format6)
        sheet.write(2, 5, 'Code', format6)
        sheet.write(2, 6, 'Product Name', format6)
        sheet.write(2, 7, 'Transfer Qty', format6)
        sheet.write(2, 8, 'MRP', format6)
        sheet.write(2, 9, 'Basic Cost', format6)
        sheet.write(2, 10, 'Basic Cost Total', format6)
        sheet.write(2, 11, 'Tax', format6)
        sheet.write(2, 12, 'L Cost', format6)
        sheet.write(2, 13, 'L Cost Total', format6)
        sheet.write(2, 14, 'Department', format6)
        sheet.write(2, 15, 'Category', format6)
        sheet.write(2, 16, 'Sub Category', format6)
        sheet.write(2, 17, 'Vendor', format6)
        sheet.write(2, 18, 'Doc Type', format6)
        
        sheet.write_merge(0, 1, 0, 7, 'Inter Branch Transfer Report',header) 

           
               
        sql = ''' select 
        branch,inter_branch,description,doc_no,to_char(movement_date,'dd/mm/yyyy'),code,product_name,
        transfer_qty,mrp,basic_cost,basic_cost_total,tax,l_cost,
        l_cost_total,department,category,sub_category,vendor,doc_type
        from ss_inter_branch_transfer_screen_line         
        where ss_inter_branch_id=(select max(ss_inter_branch_id) from ss_inter_branch_transfer_screen_line)                      
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
        export_id = self.env['ss.inter.branch.transfer.rep.excel'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        
        fp.seek(0)
        data = fp.read()
        fp.close()

        return{
              'view_mode': 'form',
              'res_id': export_id.id,
              'res_model': 'ss.inter.branch.transfer.rep.excel',

              'type': 'ir.actions.act_window',
              'context': False,

            }
        
ss_inter_branch_screen_wzd()
 
class ss_inter_btanch_screen_line(models.Model):
    _name = "ss.inter.branch.transfer.screen.line"
    _description = "Sales summary Line"
    
    ss_inter_branch_id = fields.Many2one('ss.inter.branch.transfer.screen.wzd',string='ss_inter_branch_id',ondelete='cascade')
   
    branch = fields.Char(string="Branch") 
    inter_branch = fields.Char(string="Inter Branch") 
    description = fields.Char(string="Description") 
    doc_no = fields.Char(string="Doc No")        
    movement_date = fields.Date('Movement Date')
    code = fields.Integer()
    product_name = fields.Char()
    transfer_qty = fields.Float()
    mrp = fields.Float()
    basic_cost = fields.Float()
    basic_cost_total = fields.Float()
    tax = fields.Char()
    l_cost = fields.Float()
    l_cost_total = fields.Float()
    department = fields.Char(string="Department")
    category = fields.Char()
    sub_category = fields.Char()
    vendor = fields.Char()
    doc_type = fields.Char()
           
ss_inter_btanch_screen_line()
    
     
class ss_excel_extended_inter_branch_rep(models.Model):
    _name= "ss.inter.branch.transfer.rep.excel"
    
    name = fields.Char(default="Download Excel Report")
    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64) 
    
    