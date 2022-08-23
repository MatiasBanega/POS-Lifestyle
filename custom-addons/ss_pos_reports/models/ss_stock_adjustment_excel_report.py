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


class super_stock_adjustment_bill_report(models.Model):
    _name = "super.stock.adjustment.report"
       
    start_date = fields.Date('Date From') 
    end_date = fields.Date(string="Date To") 
    company_id = fields.Many2one('res.company',string='Company',default=lambda self:self.env.company.id)
    organization_id = fields.Many2one('organization.master', string="Organization")
    ss_department = fields.Many2one('department.master',string="Department")
    ss_product_category = fields.Many2one('category.masters',string="Category")
                            
    ss_product_sub_category = fields.Many2one('sub.category.master',string="Sub Category")
    ss_product_brand = fields.Many2one('brand.master',string="Brand")
    ss_vendors = fields.Many2one('vendor.master',string="Vendor")
    
    stor_department_id_domain= fields.Char(compute="_compute_super_department_domain",readonly=True,store=False)
    
    stor_category_id_domain= fields.Char(compute="_compute_super_category_domain",readonly=True,store=False)
    
    stor_sub_category_id_domain= fields.Char(compute="_compute_super_sub_category_domain",readonly=True,store=False)

  
    @api.depends('company_id')
    def _compute_super_department_domain(self):
        for rec in self:
            rec.stor_department_id_domain = json.dumps([('org_id', '=',rec.company_id.organization_id.org_id)])
            
    @api.depends('ss_department')
    def _compute_super_category_domain(self):
        for rec in self:
            rec.stor_category_id_domain = json.dumps(
                        [('depart', '=',rec.ss_department.depart_ment_id)])
            
    @api.depends('ss_product_category')
    def _compute_super_sub_category_domain(self):
        for rec in self:
            rec.stor_sub_category_id_domain = json.dumps(
                        [('cate_gory_id', '=',rec.ss_product_category.cate)])
            
      
                          
    def print_super_stock_report(self):
        
         
        def get_line_stock(self):
            res = {}
            dict={}
            lis=[]
            start_date = self.start_date
            end_date = self.end_date
            company_id = self.company_id.name
            organization_id=self.organization_id.name
            ss_department = ''
            if self.ss_department:
                print("ssssssss")
                ss_department = "and dp.name= '%s'"%(self.ss_department.name)
            ss_product_category = ''
            if self.ss_product_category:
                print("ccccccc")
                ss_product_category = "and pc.name= '%s'"%(self.ss_product_category.name)
            ss_product_sub_category =''
            if self.ss_product_sub_category:
                print("bbbbb")
                ss_product_sub_category = "and ps.name= '%s'"%(self.ss_product_sub_category.name)
            ss_product_brand = ''
            if self.ss_product_brand:
                print("PPPPb")
                ss_product_brand =  "and b.name= '%s'"%(self.ss_product_brand.name)
            ss_vendors = ''
            if self.ss_vendors:
                print("vvvvv")
                ss_vendors = "and cb.name= '%s'"%(self.ss_vendors.name)
                print ('venodr')
            
            try:
                db_conn = self.env['db.connection'].search([('company_id','=',self.company_id.name)], limit=1)
                print('db_conn',db_conn.company_id,self.company_id)         
                db_connect=db_conn.database_connect()
                print('function',db_connect)
                cursor = db_connect.cursor()
                
                
                sqls='''
                delete from super_stock_adjustment_line
                 '''
                self.env.cr.execute(sqls)
                print('sqls',sqls)
             
                sql= '''
                        SELECT ad.value as STR_Branch,
                        i.description as STR_Description,
                        i.documentno as STR_doc_no, 
                        i.movementdate as Dt_s_Date, 
                        p.value as STR_Code,
                        p.name as STR_Product_Name,
                        round((il.qtycount-il.qtybook),2) as NUM_adjustment_qty,
                        round(p.um_mrp,2) as Mrp,
                        round(il.um_netcost,2) as L_Cost, 
                         round(il.um_netlandcost, 2) AS SUM_LCost_Total ,
                         round(il.um_grosscost2,2) as fgc,
                         round((il.qtycount - il.qtybook) * il.um_grosscost2,2) as fgc_total,
                         round(il.um_purchasevatamt,2) as tax_total, 
                         dp.name as grp_Department,
                         pc.name as STR_Category,
                         ps.name as STR_Sub_Category,
                         b.name as STR_Brand,
                         cb.name as STR_Vendor,
                         dc.printname as STR_Doc_Type, 
                         su.name as STR_SubDoc_Type, 
                         (case when i.UM_PISubType='A' then 'Addition ' 
                          when i.UM_PISubType='D' then 'Deduction '
                          when i.UM_PISubType='B' then 'Addition/Deduction'
                           end) as STR_Inv_Sub_Type 
                         FROM m_inventory i 
                        JOIN m_inventoryline il on il.m_inventory_id=i.m_inventory_id
                         JOIN c_doctype dc on dc.c_doctype_id=i.c_doctype_id 
                        JOIN m_product p on p.m_product_id=il.m_product_id
                         JOIN AD_Org ad on ad.ad_org_id=p.ad_org_id 
                        JOIN M_Product_Category pc ON pc.M_Product_Category_ID = il.M_Product_Category_ID 
                        LEFT JOIN UM_Product_SubCategory ps ON ps.UM_Product_SubCategory_ID = p.UM_Product_SubCategory_ID
                         LEFT JOIN UM_Brand b ON b.UM_Brand_ID = il.um_brand_id    
                         JOIN um_product_department dp ON dp.um_product_department_id = il.um_product_department_id  
                        left JOIN um_subdoctype su on su.um_subdoctype_id=il.um_subdoctype_id
                         LEFT JOIN m_product_po mp ON mp.m_product_id = p.m_product_id AND mp.iscurrentvendor = 'Y'::bpchar
                         LEFT JOIN c_bpartner cb on cb.c_bpartner_id = mp.c_bpartner_id   where  (i.docstatus in ('CO','CL')) and dc.name not in ('Inter Branch Transfer Send','Inter Branch Transfer receive') 
                         and i.movementdate::date  >= '%s' and i.movementdate::date <='%s' 
                       %s  %s  %s  %s  %s
                             
                 
                  ''' %(start_date,end_date,ss_department,ss_product_category,ss_product_sub_category,ss_product_brand,ss_vendors)
             
                   
                cursor.execute(sql)
                print(sql)
                super_stock_data = cursor.fetchall()
                print("super_stock_data", super_stock_data)
                
                
                  
                for row in super_stock_data:  
                    print('yyyyyyyyyyy')              
                    dict = {'STR_Branch':row[0],'STR_Description':row[1],'STR_doc_no':row[2] ,
                        'Dt_s_Date':row[3],'STR_Code':row[4] ,'STR_Product_Name':row[5],'NUM_adjustment_qty':row[6],
                        'Mrp':row[7],
                        'L_Cost':row[8],'SUM_LCost_Total':row[9],'fgc':row[10],
                        'fgc_total':row[11],'tax_total':row[12], 'grp_Department':row[13],'STR_Category':row[14],
                        'STR_Sub_Category':row[15], 'STR_Brand':row[16],'STR_Vendor':row[17],
                        'STR_Doc_Type':row[18],'STR_SubDoc_Type':row[19],'STR_Inv_Sub_Type':row[20],
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
                
                        
        
            
        sum_num_qty = 0
        sum_lcost_tot = 0
        

        
      
        stock_ad_order_line = []
        seq = 0
        
        for line in get_line_stock(self):
            print('ppppp')
            
            if line['NUM_adjustment_qty']:
                sum_num_qty+=line['NUM_adjustment_qty']
            if line['SUM_LCost_Total']:
                sum_lcost_tot+=line['SUM_LCost_Total']
             
                             
            stock_ad_order_line.append((0,0,{
                                    'ss_branch' : line['STR_Branch'],
                                    'ss_description' : line['STR_Description'],
                                    'ss_doc_number' : line['STR_doc_no'],
                                    'ss_date' : line['Dt_s_Date'],
                                    'ss_code' : line['STR_Code'],
                                    'ss_pdt_name' :line['STR_Product_Name'],
                                    'ss_adjustment_qty' : line['NUM_adjustment_qty'],
                                    'ss_mrp_rate' : line['Mrp'], 
                                    'ss_l_cost' : line['L_Cost'],
                                    'ss_l_cost_total' : line['SUM_LCost_Total'],
                                    'ss_fgc' : line['fgc'],
                                    'ss_fgc_total' : line['fgc_total'],
                                    'ss_tax_total' : line['tax_total'],
                                    'ss_depart_ment' : line['grp_Department'],
                                    'ss_category' : line['STR_Category'],
                                    'ss_sub_category' : line['STR_Sub_Category'],
                                    'ss_brand' : line['STR_Brand'],
                                    'ss_vendor' :  line['STR_Vendor'],
                                    'ss_doc_type' : line['STR_Doc_Type'],
                                    'ss_sub_doc_type' : line['STR_SubDoc_Type'],
                                    'ss_inv_sub_type' : line['STR_Inv_Sub_Type'],
                                    
       
                                    

                
                                                   
                                }))
        if stock_ad_order_line:
                stock_ad_order_line.append((0,0,{
                                    'ss_brand' :'',
                                    'ss_adjustment_qty' : sum_num_qty,
                                    'ss_l_cost' :'',
                                    'ss_l_cost_total' : sum_lcost_tot,
                                    
                                         
                                         
                                    }))    
                                 
             
        vals = {
                   
                'start_date':self.start_date,   
                'end_date':self.end_date, 
                'company_id':self.company_id.name, 
                'organization_id': self.organization_id.name,
                'ss_department' : self.ss_department.name,
                'ss_product_category' : self.ss_product_category.name,
                'ss_product_sub_category' : self.ss_product_sub_category.name,
                'ss_product_brand' : self.ss_product_brand.name,
                'ss_vendors' : self.ss_vendors.name,
              #  'organization_id': self.organization_id.name,
                'stock_ad_order_line': stock_ad_order_line,
                           
                }
        stock_report_id = self.env['super.stock.adjustment.screen.wizard'].create(vals)
    
        res = self.env['ir.model.data'].check_object_reference(
                                                'ss_pos_reports', 'view_super_stock_adjustment_report')
        return {
                'name': 'Stock Adjust Report',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'super.stock.adjustment.screen.wizard',
                'domain': [],
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': stock_report_id.id,
                }
            
            
            
        



class super_stock_screen_wizard_excel(models.Model):
    _name = "super.stock.adjustment.screen.wizard"
    _description = "Stock Summary Reports"
       
    name = fields.Char(string="Name", default="Stock Adjustment Report")
    stock_ad_order_line = fields.One2many('super.stock.adjustment.line','stock_order',string='Open Stock Line')
    start_date = fields.Date('Date From')
    end_date = fields.Date(string="Date To") 
    company_id = fields.Char(string="Company") 
    organization_id = fields.Char(string="Organization")
    ss_department = fields.Char(string="Department")
    ss_product_category = fields.Char(string="Category")
    ss_product_sub_category = fields.Char(string="Sub Category")
    ss_product_brand = fields.Char(string="Brand")
    ss_vendors = fields.Char(string="Vendor")
    
   
    def print_ss_stock_adjust_excel_report(self):
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
            ss_department = self.ss_department or ''
             
    
                
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
            
           
            sheet.write(2, 0, 'Branch', format6)
            sheet.write(2, 1, 'Description', format6)
            sheet.write(2 ,2, 'Document Number', format6)
            sheet.write(2, 3, 'Start Date', format6)
            sheet.write(2, 4, 'Code', format6)
            sheet.write(2, 5, 'Product Name', format6)
            sheet.write(2, 6, 'Adjustment Qty', format6)
            sheet.write(2, 7, 'MRP', format6)
            sheet.write(2, 8, 'L Cost', format6)
            sheet.write(2, 9, 'L Cost Total', format6) 
            sheet.write(2, 10, 'FGC', format6) 
            sheet.write(2, 11, 'FGC Total', format6) 
            sheet.write(2, 12, 'Tax Total', format6)
            sheet.write(2, 13, 'Department', format6) 
            sheet.write(2, 14, 'Category', format6) 
            sheet.write(2, 15, 'Sub Category', format6) 
            sheet.write(2, 16, 'Brand', format6)
            sheet.write(2, 17, 'Vendor', format6)
            sheet.write(2, 18, 'Document Type', format6)
            sheet.write(2, 19, 'Sub Document Type', format6)  
            sheet.write(2, 20, 'Inv Sub Type', format6)  
             
      
                                          
            sheet.write_merge(0, 1, 0, 20, 'Stock Adjustment Report',header)               
            sql = '''    
                    select ss_branch,ss_description,ss_doc_number,to_char(ss_date,'dd/mm/yyyy'),ss_code,ss_pdt_name,
                    ss_adjustment_qty,ss_mrp_rate,ss_l_cost,ss_l_cost_total,ss_fgc,ss_fgc_total,ss_tax_total,ss_depart_ment,ss_category,
                    ss_sub_category,ss_brand,ss_vendor,ss_doc_type,ss_sub_doc_type,ss_inv_sub_type from
                    super_stock_adjustment_line         
                    where stock_order=(select max(stock_order) from  super_stock_adjustment_line )
                      
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
            export_id = self.env['excel.extended.super.stock.adjust.report'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
            
            fp.seek(0)
            data = fp.read()
            fp.close()
    
            return{
                  'view_mode': 'form',
                  'res_id': export_id.id,
                  'res_model': 'excel.extended.super.stock.adjust.report',
                  'type': 'ir.actions.act_window',
                  'context': False,
                         
                }
   
super_stock_screen_wizard_excel()
 
class stock_adjustment_super_screen_line(models.Model):
    _name = "super.stock.adjustment.line"
    _description = "Stock Adjustment"
      
    s_date = fields.Date(string="Date")
    stock_order = fields.Many2one('super.stock.adjustment.screen.wizard',string='stock_order',ondelete='cascade')
    ss_branch = fields.Char(string="Branch")
    ss_description = fields.Char(string="Description")
    ss_doc_number = fields.Char(string="Document Number")
    ss_date = fields.Date(string="Start Date")
    ss_code = fields.Integer(string="Code")
    ss_pdt_name = fields.Char(string="Product Name")   
    ss_adjustment_qty = fields.Float(string="Adjustment Qty")
    ss_mrp_rate = fields.Float(string="MRP")
    ss_l_cost = fields.Float(string="L Cost")
    ss_l_cost_total = fields.Float(string="L Cost Total")
    ss_fgc = fields.Float(string="FGC")
    ss_fgc_total = fields.Float(string="FGC Total")
    ss_tax_total = fields.Float(string="Tax Total")
    ss_depart_ment = fields.Char(string="Department")
    ss_category = fields.Char(string="Category")
    ss_sub_category = fields.Char(string="Sub Category")
    ss_brand = fields.Char(string="Brand")
    ss_vendor = fields.Char(string="Vendor")
    ss_doc_type = fields.Char(string="Document Type")
    ss_sub_doc_type = fields.Char(string="Sub Document Type")
    ss_inv_sub_type = fields.Char(string="Inv Sub Type")
            
stock_adjustment_super_screen_line()    

class excel_extended_super_stock_report(models.Model):
    _name= "excel.extended.super.stock.adjust.report"
    
    name = fields.Char(default="Download Excel Report")
    excel_file = fields.Binary('Download Report Excel')
    file_name = fields.Char('Excel File', size=64) 
    

