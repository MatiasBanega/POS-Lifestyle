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

DATE_FORMAT_1 = "%Y-%d-%m"
DATE_FORMAT_2 = "%d/%m/%y"
DATE_FORMAT_3 = "%m/%d/%y"

class product_design(models.Model):
    _name = "product.design.view"
       
    start_date = fields.Date('Date From') #, required=True
    end_date = fields.Date(string="Date To")
    company=fields.Many2one('res.company',string="Company") #, required=True
   
    def get_product_design(self):

        def get_lines(self):
            res = {}
            dict={}
            lis=[]
            start_date = self.start_date
            end_date = self.end_date
            company=self.company.name
            
            try:
                db_conn = self.env['db.connection'].search([])        
                db_connect=db_conn.database_connect()
                cursor = db_connect.cursor() 
            
                sqls='''
     
                  delete from product_design_master
                   '''
                                     
                self.env.cr.execute(sqls)
                
                sql='''
     
                  select name from um_productdesign

                   '''
                                  
                cursor.execute(sql)
                sale_data = cursor.fetchall()
                for row in sale_data:                
                    dict = {'name':row[0],}
                    lis.append(dict)
                return lis
            except (Exception, psycopg2.Error) as error:
                raise UserError(_("Error while fetching data from PostgreSQL "))

            finally:
    # closing database connection.
                if db_conn:
                    cursor.close()
                    db_connect.close()
                    
    
        sum_amt = 0
        tot_amt = 0
        product_design_line = []
        seq = 0
        for line in get_lines(self):
                         
            product_design_line.append((0,0,{
                                'name' : line['name'],
                                
                                     }))
        if product_design_line:
            product_design_line.append((0,0,{
                                }))    
                            
         
        vals = {
                 'product_design_line': product_design_line,
                }
        product_design_id = self.env['product.design.wzd'].create(vals)

        res = self.env['ir.model.data'].check_object_reference(
                                            'lifestyle_masters', 'product_design_wizard')
        return {
                    'name': '',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'product.design.wzd',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                     'res_id': product_design_id.id,
            }
       
class product_design_wzd(models.Model):
    _name = "product.design.wzd"
    _description = "Product Design Wizard"
    
    
    name = fields.Char(default="Product Design Wizard")
    product_design_line = fields.One2many('product.design.master','attribute_id',string='Open Order Line')
    start_date = fields.Date('Date From') #, required=True
    end_date = fields.Date(string="Date To")
    company = fields.Char('Company')
    

product_design_wzd()
 
class ProductDesignMaster(models.Model):
    _name = "product.design.master"
    _description = "Product Design Master"
    
    attribute_id = fields.Many2one('product.design.wzd',string='attribute_id',ondelete='cascade')
    name = fields.Char(string="Product Design")
    
     
           
ProductDesignMaster()
    
     
  
    
