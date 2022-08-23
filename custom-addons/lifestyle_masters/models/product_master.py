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

class Product(models.Model):
    _name = "product.view"
       
    start_date = fields.Date('Date From') #, required=True
    end_date = fields.Date(string="Date To")
    company=fields.Many2one('res.company',string="Company") #, required=True
   
    def get_product(self):

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
     
                  delete from product_master
                   '''
                                      
                self.env.cr.execute(sqls)
                
                sql='''
     
                  select name from m_product

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
        product_line = []
        seq = 0
        for line in get_lines(self):
                         
            product_line.append((0,0,{
                                'name' : line['name'],
                                
                                     }))
        if product_line:
            product_line.append((0,0,{
                                }))    
                            
         
        vals = {
                 'product_line': product_line,
                }
        product_id = self.env['product.wzd'].create(vals)

        res = self.env['ir.model.data'].check_object_reference(
                                            'lifestyle_masters', 'product_wizard')
        return {
                    'name': '',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'product.wzd',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                     'res_id': product_id.id,
            }
       
class product_wzd(models.Model):
    _name = "product.wzd"
    _description = "Product Wizard"
    
    
    name = fields.Char(default="Product Wizard")
    product_line = fields.One2many('product.master','attribute_id',string='Open Order Line')
    start_date = fields.Date('Date From') #, required=True
    end_date = fields.Date(string="Date To")
    company = fields.Char('Company')
    

product_wzd()
 
class ProductMaster(models.Model):
    _name = "product.master"
    _description = "product Master"
    
    attribute_id = fields.Many2one('product.wzd',string='attribute_id',ondelete='cascade')
    name = fields.Char(string="Product")
    
     
           
ProductMaster()
    
     
  
    
