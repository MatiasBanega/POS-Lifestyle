from dateutil.relativedelta import relativedelta
from odoo import  fields, models 
from odoo.exceptions import UserError
import io, base64, re
import xlsxwriter, xlwt, psycopg2
from odoo import exceptions, _

DATE_FORMAT_1 = "%d-%m-%y"
DATE_FORMAT_2 = "%m/%d/%y"
DATE_FORMAT_3 = "%y/%m/%d"

class inter_branch_transfer_wzd(models.Model):
    _name = "inter.branch.transfer.report"
       
    start_date = fields.Date() 
    end_date = fields.Date()
    company = fields.Many2one('res.company',string='Company',default=lambda self:self.env.company.id)
        
    def print_inter_branch_report(self):

        def get_lines(self):
            dict = {}
            lis = []
            start_date = self.start_date
            end_date = self.end_date
            company = self.company.name
            try:
                db_conn = self.env['db.connection'].search([('company_id','=',self.company.id)], limit=1)

                db_connect=db_conn.database_connect()

                cursor = db_connect.cursor() 
            
                sql='''
                      select 
                        o.value as STR_Branch,
                        b.name as STR_Inter_Branch,
                        i.description as STR_Description,
                        i.documentno as STR_doc_no,
                        i.movementdate as movement_date,
                        p.value as STR_Code,
                        p.name as STR_Product_Name,
                        br.name as STR_Brand,
                        pd.name as STR_Product_Design,
                        it.name as STR_Item_Type,
                        pdc.name as STR_Product_Color,
                        pds.name as STR_Product_Size,
                        abs(round((il.qtycount-il.qtybook),2)) as NUM_transfer_qty,
                        round(il.um_mrp,2) as NUM_Mrp,
                        round(il.um_basiccost,2) as NUM_basiccost,
                        abs(round((il.um_basiccost*(il.qtycount-il.qtybook)),2)) as NUM_basiccost_total,
                        t.name as STR_tax,
                        abs(round(il.um_netcost,2)) as NUM_L_Cost,
                        abs(round(il.um_netlandcost, 2)) AS NUM_LCost_Total ,
                        dp.name as STR_Department,
                        pc.name as STR_Category,
                        ps.name as STR_Sub_Category,
                        cb.name as STR_Vendor,
                        dc.printname as STR_Doc_Type
                        from m_inventory i
                        join m_inventoryline il on i.m_inventory_id=il.m_inventory_id
                        join ad_org o on o.ad_org_id=i.ad_org_id
                        left join UM_branch b on b.UM_branch_ID = i.UM_branch_ID
                        JOIN c_doctype dc on dc.c_doctype_id=i.c_doctype_id
                        join m_product p on p.m_product_id=il.m_product_id
                        JOIN um_product_department dp ON dp.um_product_department_id = il.um_product_department_id
                        JOIN M_Product_Category pc ON pc.M_Product_Category_ID = il.M_Product_Category_ID
                        LEFT JOIN UM_Product_SubCategory ps ON ps.UM_Product_SubCategory_ID = p.UM_Product_SubCategory_ID
                        left JOIN um_subdoctype su on su.um_subdoctype_id=il.um_subdoctype_id
                        left join c_taxcategory t on t.c_taxcategory_id=il.um_purchasetaxcategory_id
                        join um_productattribute pa on pa.um_productattribute_id=il.um_productattribute_id
                        left join UM_Brand br on br.um_brand_id=pa.um_brand_id
                        left join um_productdesign pd on pd.um_productdesign_id=pa.um_productdesign_id
                        left join um_itemtype it on it.um_itemtype_id=pa.um_itemtype_id
                        left join um_productcolor pdc on pdc.um_productcolor_id=pa.um_productcolor_id
                        left join um_productsize pds on pds.um_productsize_id=pa.um_productsize_id
                        join um_batchprice bp on bp.m_product_id=p.m_product_id  and bp.um_productattribute_id=pa.um_productattribute_id
                        and bp.m_attributesetinstance_id=il.m_attributesetinstance_id
                        left JOIN c_bpartner cb on cb.c_bpartner_id=bp.c_bpartner_id
                        where i.c_doctype_id in (select c_doctype_id from c_doctype where name in
                        ('Inter Branch Transfer Receive','Inter Branch Transfer Send'))
                        and (i.docstatus in ('CO','CL')) 
                        and i.movementdate::date >= '%s' and i.movementdate::date <= '%s'
                        order by i.movementdate              
                      '''%(start_date, end_date)
                
            
                cursor.execute(sql)

                sale_data = cursor.fetchall()

                for row in sale_data:                
                    dict = {'branch':row[0],'inter_branch':row[1] , 'description':row[2],'doc_no':row[3] ,
                            'movement_date':row[4],'code':row[5],'product_name':row[6],'brand':row[7],
                            'product_design':row[8],'item_type':row[9],'product_color':row[10],
                            'product_size':row[11],'transfer_qty':row[12],
                            'mrp':row[13],'basic_cost':row[14] , 'basic_cost_total':row[15],'tax':row[16] ,
                            'l_cost':row[17],'l_cost_total':row[18],'department':row[19],'category':row[20],
                            'sub_category':row[21],'vendor':row[22],'doc_type':row[23]}
                        

                    lis.append(dict)

                return lis            
            except (Exception, psycopg2.Error) as error:
                raise UserError(_("Error while fetching data from PostgreSQL "))

            finally:
    # closing database connection.
                if db_conn:
                    cursor.close()

                    db_connect.close()

                    
        inter_branch_order_line = []
        transfer_qty_tot = 0
        mrp_tot = 0
        basic_cost_tot = 0
        basic_cost_total_tot = 0
        l_cost_tot = 0
        l_cost_total_tot = 0
        for line in get_lines(self):
            if line['transfer_qty']:
                transfer_qty_tot+=line['transfer_qty']
            if line['mrp']:
                mrp_tot+=line['mrp']
            if line['basic_cost']:
                basic_cost_tot+=line['basic_cost']
            if line['basic_cost_total']:
                basic_cost_total_tot+=line['basic_cost_total']
            if line['l_cost']:
                l_cost_tot+=line['l_cost']
            if line['l_cost_total']:
                l_cost_total_tot+=line['l_cost_total']             
            inter_branch_order_line.append((0,0,{
                                'branch' : line['branch'],
                                'inter_branch' : line['inter_branch'],
                                'description' : line['description'],
                                'doc_no' : line['doc_no'],
                                'movement_date' : line['movement_date'],
                                'code' : line['code'],
                                'product_name' : line['product_name'],
                                'brand' : line['brand'],
                                'product_design' : line['product_design'],
                                'item_type' : line['item_type'],
                                'product_color' : line['product_color'],
                                'product_size' : line['product_size'],
                                'transfer_qty' : line['transfer_qty'],
                                'mrp' : line['mrp'],
                                'basic_cost' : line['basic_cost'],
                                'basic_cost_total' : line['basic_cost_total'],
                                'tax' : line['tax'],
                                'l_cost' : line['l_cost'],
                                'l_cost_total' : line['l_cost_total'],
                                'department' : line['department'],
                                'category' : line['category'],
                                'sub_category' : line['sub_category'],
                                'vendor' : line['vendor'],
                                'doc_type' : line['doc_type'],
                                     }))
        if inter_branch_order_line:
            inter_branch_order_line.append((0,0,{  
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
               'inter_branch_order_line': inter_branch_order_line,

                }
        inter_branch_transfer_report_id = self.env['inter.branch.transfer.screen.wzd'].create(vals)

        res = self.env['ir.model.data'].check_object_reference(
                                            'ls_pos_reports', 'view_item_branch_transfer_wzd_report')
        return {
                    'name': 'department Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'inter.branch.transfer.screen.wzd',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': inter_branch_transfer_report_id.id,
            }
       
class sales_screen_wzd(models.Model):
    _name = "inter.branch.transfer.screen.wzd"
    _description = "Department Sales Orders Summary Reports"
    
    name = fields.Char(default="Inter Branch Transfer Report")
    inter_branch_order_line = fields.One2many('inter.branch.transfer.screen.line','inter_branch_id',string='Open Order Line')
    start_date = fields.Date('Date From')
    end_date = fields.Date("Date TO")
    company = fields.Char(string="Company")

    def print_inter_branch_ternsfer_excel_report(self):
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
#         partner_id = self.partner_id or ''
            
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
        sheet.write(2, 7, 'Brand', format6)
        sheet.write(2, 8, 'Product Design', format6)
        sheet.write(2, 9, 'Item Type', format6)
        sheet.write(2, 10, 'Product Color', format6)
        sheet.write(2, 11, 'Product Size', format6)
        sheet.write(2, 12, 'Transfer Qty', format6)
        sheet.write(2, 13, 'MRP', format6)
        sheet.write(2, 14, 'Basic Cost', format6)
        sheet.write(2, 15, 'Basic Cost Total', format6)
        sheet.write(2, 16, 'Tax', format6)
        sheet.write(2, 17, 'L Cost', format6)
        sheet.write(2, 18, 'L Cost Total', format6)
        sheet.write(2, 19, 'Department', format6)
        sheet.write(2, 20, 'Category', format6)
        sheet.write(2, 21, 'Sub Category', format6)
        sheet.write(2, 22, 'Vendor', format6)
        sheet.write(2, 23, 'Doc Type', format6)
        
        sheet.write_merge(0, 1, 0, 2, 'Inter Branch Transfer Report',header) 

           
               
        sql = ''' select 
        branch,inter_branch,description,doc_no,to_char(movement_date,'dd/mm/yyyy'),code,product_name,brand,product_design,
        item_type,product_color,product_size,transfer_qty,mrp,basic_cost,basic_cost_total,tax,l_cost,
        l_cost_total,department,category,sub_category,vendor,doc_type
        from inter_branch_transfer_screen_line         
        where inter_branch_id=(select max(inter_branch_id) from inter_branch_transfer_screen_line)                      
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
        export_id = self.env['inter.branch.transfer.rep.excel'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        
        fp.seek(0)
        data = fp.read()
        fp.close()

        return{
              'view_mode': 'form',
              'res_id': export_id.id,
              'res_model': 'inter.branch.transfer.rep.excel',

              'type': 'ir.actions.act_window',
              'context': False,
          
            }
        
sales_screen_wzd()
 
class department_orders_screen_line(models.Model):
    _name = "inter.branch.transfer.screen.line"
    _description = "Sales summary Line"
    
    inter_branch_id = fields.Many2one('inter.branch.transfer.screen.wzd',string='inter_branch_id',ondelete='cascade')
   
    branch = fields.Char(string="Branch") 
    inter_branch = fields.Char(string="Inter Branch") 
    description = fields.Char(string="Description") 
    doc_no = fields.Char(string="Doc No")        
    movement_date = fields.Date('Movement Date')
    code = fields.Integer()
    product_name = fields.Char()
    brand = fields.Char()
    product_design = fields.Char()
    item_type = fields.Char()
    product_color = fields.Char()
    product_size = fields.Char()
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
           
department_orders_screen_line()
    
     
class excel_extended_sales_open_orders_rep(models.Model):
    _name= "inter.branch.transfer.rep.excel"
    
    name = fields.Char(default="Inter Branch Transfer Report")
    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64) 
    
    