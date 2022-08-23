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


class stock_adjustment_bill_report(models.Model):
    _name = "stock.adjustment.report"
       
    start_date = fields.Date('Date From') 
    end_date = fields.Date(string="Date To") 
    company_id = fields.Many2one('res.company',string='Company',default=lambda self:self.env.company.id)
    department = fields.Many2one('department.master',string="Department")
    product_category = fields.Many2one('category.masters',string="Category")
                            
    product_sub_category = fields.Many2one('sub.category.master',string="Sub Category")
    product_brand = fields.Many2one('brand.master',string="Brand")
    vendors = fields.Many2one('vendor.master',string="Vendor")
    
    department_id_domain= fields.Char(compute="_compute_department_domain",readonly=True,store=False)
    
    category_id_domain= fields.Char(compute="_compute_category_domain",readonly=True,store=False)
    
    sub_category_id_domain= fields.Char(compute="_compute_sub_category_domain",readonly=True,store=False)

  
    @api.depends('company_id')
    def _compute_department_domain(self):
        for rec in self:
            rec.department_id_domain = json.dumps([('org_id', '=',rec.company_id.organization_id.org_id)])
            
    @api.depends('department')
    def _compute_category_domain(self):
        for rec in self:
            rec.category_id_domain = json.dumps(
                        [('depart', '=',rec.department.depart_ment_id)])
            
    @api.depends('product_category')
    def _compute_sub_category_domain(self):
        for rec in self:
            rec.sub_category_id_domain = json.dumps(
                        [('cate_gory_id', '=',rec.product_category.cate)])
            
      
        
                          
    def print_stock_report(self):
        
         
        def get_stock_lines(self):
            res = {}
            dict={}
            lis=[]
            start_date = self.start_date
            end_date = self.end_date
            company_id = self.company_id.name
            department = ''
            if self.department:
                print("ssssssss")
                department = "and dp.name= '%s'"%(self.department.name)
            product_category = ''
            if self.product_category:
                print("ccccccc")
                product_category = "and pc.name= '%s'"%(self.product_category.name)
            product_sub_category =''
            if self.product_sub_category:
                print("bbbbb")
                product_sub_category = "and ps.name= '%s'"%(self.product_sub_category.name)
            product_brand = ''
            if self.product_brand:
                print("PPPPb")
                product_brand =  "and bd.name= '%s'"%(self.product_brand.name)
            vendors = ''
            if self.vendors:
                print("vvvvv")
                vendors = "and cb.name= '%s'"%(self.vendors.name)
                print ('venodr')
            
            try:
                db_conn = self.env['db.connection'].search([('company_id','=',self.company_id.name)], limit=1)
                print('db_conn',db_conn.company_id,self.company_id)         
                db_connect=db_conn.database_connect()
                print('function',db_connect)
                cursor = db_connect.cursor()
                
                sqls='''
                delete from stock_adjustment_line
                 '''
                self.env.cr.execute(sqls)
                print('sqls',sqls)
             
                sql= '''
                   SELECT ad.value as STR_Branch,i.description as STR_Description,i.documentno as STR_doc_no, i.movementdate as Dt_s_Date,
                    p.value as STR_Code,p.name as STR_Product_Name,bd.name as STR_brand,
                    it.name as STR_itemtype, d.name as STR_productdesign, c.name as STR_productcolor, si.name as STR_productsize,round((il.qtycount-il.qtybook),2) as NUM_adjustment_qty,round(il.um_mrp,2) as Mrp,round(il.um_netcost,2) as L_Cost,round(il.um_netlandcost, 2) AS SUM_LCost_Total,
                    round(il.um_grosscost2,2) as fgc,round(il.qtycount*il.um_grosscost2,2) as fgc_total,round(il.um_purchasevatamt,2) as tax_total,
                      dp.name as grp_Department,pc.name as STR_Category,ps.name as STR_Sub_Category,
                    cb.name as STR_Vendor,dc.printname as STR_Doc_Type,su.name as STR_SubDoc_Type,
                         (case when i.UM_PISubType='A' then 'Addition'
                          when i.UM_PISubType='D' then 'Deduction'
                          when i.UM_PISubType='B' then 'Addition/Deduction'
                         end) as STR_Inv_Sub_Type
                     FROM m_inventory i
                    JOIN m_inventoryline il on il.m_inventory_id=i.m_inventory_id
                    JOIN c_doctype dc on dc.c_doctype_id=i.c_doctype_id
                    JOIN m_product p on p.m_product_id=il.m_product_id
                    JOIN um_productattribute pa on pa.um_productattribute_id=il.um_productattribute_id
                    LEFT JOIN UM_Brand bd ON bd.UM_Brand_ID = pa.UM_Brand_ID
                    LEFT JOIN UM_itemtype it ON it.UM_itemtype_id = pa.UM_itemtype_id
                    LEFT JOIN um_productdesign d ON d.um_productdesign_id = pa.um_productdesign_id
                    LEFT JOIN um_productcolor c ON c.um_productcolor_id = pa.um_productcolor_id
                    LEFT JOIN um_productsize si ON si.um_productsize_id = pa.um_productsize_id  
                    JOIN AD_Org ad on ad.ad_org_id=p.ad_org_id
                    JOIN M_Product_Category pc ON pc.M_Product_Category_ID = il.M_Product_Category_ID
                    LEFT JOIN UM_Product_SubCategory ps ON ps.UM_Product_SubCategory_ID = p.UM_Product_SubCategory_ID
                    JOIN um_product_department dp ON dp.um_product_department_id = il.um_product_department_id
                    left JOIN um_subdoctype su on su.um_subdoctype_id=il.um_subdoctype_id
                    JOIN um_batchprice bp on bp.m_product_id=p.m_product_id and bp.um_productattribute_id=pa.um_productattribute_id
                    and bp.m_attributesetinstance_id=il.m_attributesetinstance_id
                    left JOIN c_bpartner cb on cb.c_bpartner_id=bp.c_bpartner_id
                    where  (i.docstatus in ('CO','CL')) and
                     i.movementdate::date  >= '%s' and i.movementdate::date <='%s' 
                     %s  %s  %s  %s  %s
                                       
                    
                    and i.c_doctype_id not in (select c_doctype_id from c_doctype where name in ('Approval In','Approval Out',
                    'Inter Branch Transfer Send','Inter Branch Transfer Receive'))
                   group by ad.value,i.description,i.documentno,Dt_s_Date,p.value,p.name,bd.name,it.name,d.name,c.name,si.name,NUM_adjustment_qty,
                 Mrp,L_Cost,SUM_LCost_Total,fgc,fgc_total,tax_total,dp.name,pc.name, ps.name, cb.name,dc.printname ,su.name,STR_Inv_Sub_Type  

                    order by  i.movementdate
                 
                  ''' %(start_date,end_date,department,product_category,product_sub_category,product_brand,vendors)
             
                 
                cursor.execute(sql)
                print(sql)
                stock_data = cursor.fetchall()
                print("stock_data", stock_data)
                
                
                  
                for row in stock_data:  
                    print('yyyyyyyyyyy')              
                    dict = {'STR_Branch':row[0],'STR_Description':row[1],'STR_doc_no':row[2] ,
                        'Dt_s_Date':row[3],'STR_Code':row[4] ,'STR_Product_Name':row[5],'STR_brand':row[6],
                        'STR_itemtype':row[7],
                        'STR_productdesign':row[8],'STR_productcolor':row[9],'STR_productsize':row[10],
                        'NUM_adjustment_qty':row[11],'Mrp':row[12], 'L_Cost':row[13],'SUM_LCost_Total':row[14],
                        'fgc':row[15], 'fgc_total':row[16],'tax_total':row[17],
                        'grp_Department':row[18],'STR_Category':row[19],'STR_Sub_Category':row[20],'STR_Vendor':row[21],'STR_Doc_Type':row[22],
                        'STR_SubDoc_Type':row[23],'STR_Inv_Sub_Type':row[24],
                        }
                    print('dictionary',dict)
                    lis.append(dict)
                print('list',lis)
                return lis
            except (Exception, psycopg2.Error) as error:
                raise UserError(_("Error while fetching data from PostgreSQL "))
                print("Error while fetching data from PostgreSQL", error)
      
            finally:
    # closing database connection.
                if db_conn:
                    cursor.close()
                    print('db_connect',db_connect)
                    print('close',db_connect.close)
                    db_connect.close()
                    print('db_connect1',db_connect)
                    print('close1',db_connect.close)
                    print("PostgreSQL connection is closed")
                
                        
        
            
        sum_qty = 0
        sum_lcost = 0
        

        
      
        stock_order_line = []
        seq = 0
        
        for line in get_stock_lines(self):
            print('ppppp')
            
            if line['NUM_adjustment_qty']:
                sum_qty+=line['NUM_adjustment_qty']
            if line['SUM_LCost_Total']:
                sum_lcost+=line['SUM_LCost_Total']
             
                             
            stock_order_line.append((0,0,{
                                    'branch' : line['STR_Branch'],
                                    'description' : line['STR_Description'],
                                    'doc_number' : line['STR_doc_no'],
                                    's_date' : line['Dt_s_Date'],
                                    'code' : line['STR_Code'],
                                    'pdt_name' :line['STR_Product_Name'],
                                    'brand' : line['STR_brand'],
                                    'itemtype' : line['STR_itemtype'],
                                    'pdt_design': line['STR_productdesign'],
                                    'pdt_color': line['STR_productcolor'],
                                    'pdt_size' : line['STR_productsize'],
                                    'adjustment_qty' : line['NUM_adjustment_qty'],
                                    'mrp_rate' : line['Mrp'], 
                                    'l_cost' : line['L_Cost'],
                                    'l_cost_total' : line['SUM_LCost_Total'],
                                    'fgc' : line['fgc'],
                                    'fgc_total' : line['fgc_total'],
                                    'tax_total' : line['tax_total'],
                                    'depart_ment' : line['grp_Department'],
                                    'category' : line['STR_Category'],
                                    'sub_category' : line['STR_Sub_Category'],
                                    'vendor' :  line['STR_Vendor'],
                                    'doc_type' : line['STR_Doc_Type'],
                                    'sub_doc_type' : line['STR_SubDoc_Type'],
                                    'inv_sub_type' : line['STR_Inv_Sub_Type'],
                                    
       
                                    

                
                                                   
                                }))
        if stock_order_line:
                stock_order_line.append((0,0,{
                                    'brand' :'',
                                    'adjustment_qty' : sum_qty,
                                    'l_cost' :'',
                                    'l_cost_total' : sum_lcost,
                                    
                                         
                                         
                                    }))    
                                 
             
        vals = {
                   
                'start_date':self.start_date,   
                'end_date':self.end_date,  
                'company_id':self.company_id.name,
                'department' : self.department.name,
                'product_category' : self.product_category.name,
                'product_sub_category' : self.product_sub_category.name,
                'product_brand' : self.product_brand.name,
                'vendors' : self.vendors.name,
              #  'organization_id': self.organization_id.name,
                'stock_order_line': stock_order_line,
                           
                }
        stock_bill_report_id = self.env['stock.adjustment.screen.wizard'].create(vals)
    
        res = self.env['ir.model.data'].check_object_reference(
                                                'ls_pos_reports', 'view_stock_adjustment_report')
        return {
                'name': 'Stock Adjust Report',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.adjustment.screen.wizard',
                'domain': [],
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': stock_bill_report_id.id,
                }
            
            
            
        



class stock_screen_wizard_excel(models.Model):
    _name = "stock.adjustment.screen.wizard"
    _description = "Stock Summary Reports"
       
    name = fields.Char(string="Name", default="Stock Adjustment Report")
    stock_order_line = fields.One2many('stock.adjustment.line','stock_id',string='Open Stock Line')
    start_date = fields.Date('Date From')
    end_date = fields.Date(string="Date To") 
    company_id = fields.Char(string="Company") 
    department = fields.Char(string="Department")
    product_category = fields.Char(string="Category")
    product_sub_category = fields.Char(string="Sub Category")
    product_brand = fields.Char(string="Brand")
    vendors = fields.Char(string="Vendor")
    
   
    def print_stock_adjust_excel_report(self):
            filename= 'Stock Adjustment Report.xls'
            workbook= xlwt.Workbook(encoding="UTF-8")
            
            style_header = xlwt.easyxf('pattern: pattern solid, fore_colour light_orange;'
                                   'font: bold on; font:height 230; align: wrap No; borders: left thin, right thin, top thin, bottom thin;')
            style = xlwt.easyxf('font:height 230; align: wrap No;borders: left thin, right thin, top thin, bottom thin;')
            header=xlwt.easyxf('pattern: pattern solid, fore_colour light_orange;''font:height 400; align: horiz center;font:bold True;' "borders: top thin,bottom thin , left thin, right thin")
            style = xlwt.easyxf('font:height 230; align: wrap No;')
            base_style = xlwt.easyxf('align: wrap yes')
            date_style = xlwt.easyxf('align: wrap yes', num_format_str='DD-MM-YYYY')
            datetime_style = xlwt.easyxf('align: wrap yes', num_format_str='DD-MM-YYYY HH:mm:SS')
            sheet= workbook.add_sheet('Stock Adjustment Report')
            format6 = xlwt.easyxf('pattern: pattern solid, fore_colour light_yellow;''font:height 210,bold True;align: horiz left;'"borders: top thin,bottom thin , left thin, right thin")
            format1 = xlwt.easyxf('font: bold off, color black;\
                         borders: top_color black, bottom_color black, right_color black, left_color black,\
                                  left thin, right thin, top thin, bottom thin;\
                         pattern: pattern solid, fore_color white;')
            
            
            end_date = self.end_date  or ''
            start_date = self.start_date or ''
            company_id = self.company_id or ''
            department = self.department or ''
             
    
                
            sheet.col(0).width = 800*5
            sheet.col(1).width = 800*5
            sheet.col(2).width = 800*5
            sheet.col(3).width = 800*5
            sheet.col(4).width = 800*5
            sheet.col(5).width = 800*5
            sheet.col(6).width = 800*5
            sheet.col(7).width = 800*5 
            sheet.col(8).width = 800*5
            sheet.col(9).width = 800*5
            sheet.col(10).width = 800*5
            sheet.col(11).width = 800*5
            sheet.col(12).width = 800*5
            sheet.col(13).width = 800*5
            sheet.col(14).width = 800*5
            sheet.col(15).width = 800*5
            sheet.col(16).width = 800*5
            sheet.col(17).width = 800*5
            sheet.col(18).width = 800*5
            sheet.col(19).width = 800*5
            sheet.col(20).width = 800*5
            sheet.col(21).width = 800*5
            sheet.col(22).width = 800*5
            sheet.col(23).width = 800*5
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
           
            sheet.write(2, 0, 'Branch', format6)
            sheet.write(2, 1, 'Description', format6)
            sheet.write(2 ,2, 'Document Number', format6)
            sheet.write(2, 3, 'Start Date', format6)
            sheet.write(2, 4, 'Code', format6)
            sheet.write(2, 5, 'Product Name', format6)
            sheet.write(2, 6, 'Brand', format6)
            sheet.write(2, 7, 'Item Type', format6)  
            sheet.write(2, 8, 'Product Design', format6)
            sheet.write(2, 9, 'Product Color', format6)
            sheet.write(2, 10, 'Product Size', format6)
            sheet.write(2, 11, 'Adjustment Qty', format6)
            sheet.write(2, 12, 'MRP', format6)
            sheet.write(2, 13, 'L Cost', format6)
            sheet.write(2, 14, 'L Cost Total', format6) 
            sheet.write(2, 15, 'FGC', format6) 
            sheet.write(2, 16, 'FGC Total', format6) 
            sheet.write(2, 17, 'Tax Total', format6)
            sheet.write(2, 18, 'Department', format6) 
            sheet.write(2, 19, 'Category', format6) 
            sheet.write(2, 20, 'Sub Category', format6) 
            sheet.write(2, 21, 'Vendor', format6)
            sheet.write(2, 22, 'Document Type', format6)
            sheet.write(2, 23, 'Sub Document Type', format6)  
            sheet.write(2, 24, 'Inv Sub Type', format6)  
             
      
                                          
            sheet.write_merge(0, 1, 0, 23, 'Stock Adjustment Report',header)               
            sql = '''    
                    select branch,description,doc_number,to_char(s_date,'dd/mm/yyyy'),code,pdt_name,brand,itemtype,pdt_design,pdt_color,pdt_size,
                   
                    adjustment_qty,mrp_rate,l_cost,l_cost_total,fgc,fgc_total,tax_total,depart_ment,category,
                    sub_category,vendor,doc_type,sub_doc_type,inv_sub_type from
                    stock_adjustment_line         
                    where stock_id=(select max(stock_id) from  stock_adjustment_line )
                      
                '''
        
        # pdt_size,
               
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
            export_id = self.env['excel.extended.stock.adjust.report'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
            
            fp.seek(0)
            data = fp.read()
            fp.close()
    
            return{
                  'view_mode': 'form',
                  'res_id': export_id.id,
                  'res_model': 'excel.extended.stock.adjust.report',
                  'type': 'ir.actions.act_window',
                  'context': False,
                         
                }
            
   
stock_screen_wizard_excel()
       
  
  
  
  
  
  
  
class stock_adjustment_screen_line(models.Model):
    _name = "stock.adjustment.line"
    _description = "Stock Adjustment "
      
    date = fields.Date(string="Date")
    stock_id = fields.Many2one('stock.adjustment.screen.wizard',string='stock_id',ondelete='cascade')
    branch = fields.Char(string="Branch")
    description = fields.Char(string="Description")
    doc_number = fields.Char(string="Document Number")
    s_date = fields.Date(string="Start Date")
    code = fields.Integer(string="Code")
    pdt_name = fields.Char(string="Product Name")
    brand = fields.Char(string="Brand")
    itemtype = fields.Char(string="Item Type")
    pdt_design = fields.Char(string="Product Design")
    pdt_color = fields.Char(string="Product Color")
    pdt_size = fields.Char(string="Product Size")
    adjustment_qty = fields.Float(string="Adjustment Qty")
    mrp_rate = fields.Float(string="MRP")
    l_cost = fields.Float(string="L Cost")
    l_cost_total = fields.Float(string="L Cost Total")
    fgc = fields.Float(string="FGC")
    fgc_total = fields.Float(string="FGC Total")
    tax_total = fields.Float(string="Tax Total")
    depart_ment = fields.Char(string="Department")
    category = fields.Char(string="Category")
    sub_category = fields.Char(string="Sub Category")
    vendor = fields.Char(string="Vendor")
    doc_type = fields.Char(string="Document Type")
    sub_doc_type = fields.Char(string="Sub Document Type")
    inv_sub_type = fields.Char(string="Inv Sub Type")
      
  
      
             
stock_adjustment_screen_line()    


class excel_extended_stock_report(models.Model):
    _name= "excel.extended.stock.adjust.report"
    
    name = fields.Char(default="Download Excel Report")
    excel_file = fields.Binary('Download Report Excel')
    file_name = fields.Char('Excel File', size=64) 
    

