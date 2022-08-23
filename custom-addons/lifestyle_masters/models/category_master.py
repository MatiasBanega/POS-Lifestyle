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

class Category(models.Model):
    _name = "category.view"
       
    start_date = fields.Date('Date From') #, required=True
    end_date = fields.Date(string="Date To")
    company=fields.Char(string="Company",default=lambda self: self.env.company.name) #, required=True
   
    def get_category(self):

        def get_lines(self):
            res = {}
            dict={}
            lis=[]
            start_date = self.start_date
            end_date = self.end_date
            company=self.company
            
            try:
                db_conn = self.env['db.connection'].search([])
                for rec in db_conn:    
                    db_connect=rec.database_connect()
                    cursor = db_connect.cursor() 
                
                    sqls='''
         
                      delete from category_masters
                       '''
                                      
                    self.env.cr.execute(sqls)
                    
                    sql='''
         
                      
                      select name,ad_org_id as org_id,um_product_department_id as department_id,
                      m_product_category_id as category_id   from m_product_category
                     where um_product_department_id IS NOT NULL; 
    
                       '''
                         
                                   
                    cursor.execute(sql)
                    sale_data = cursor.fetchall()
                    for row in sale_data:                
                        dict = {'name':row[0],'org_id':row[1],'department_id':row[2],'category_id':row[3],}
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
        category_line = []
        seq = 0
        for line in get_lines(self):
                         
            category_line.append((0,0,{
                                'name' : line['name'],
                                'org_id' : line['org_id'],
                                'depart' : line['department_id'],
                                'cate' : line['category_id']
                                     }))
        if category_line:
            category_line.append((0,0,{
                                }))    
                            
         
        vals = {
                 'category_line': category_line,
                    
                }
        category_id = self.env['category.wzd'].create(vals)

        res = self.env['ir.model.data'].check_object_reference(
                                            'lifestyle_masters', 'category_wizard')
        return {
                    'name': '',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'category.wzd',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': category_id.id,
            }
       
class category_wzd(models.Model):
    _name = "category.wzd"
    _description = "category Wizard"
    
    
    name = fields.Char(default="category Wizard")
    category_line = fields.One2many('category.masters','attribute_id',string='Open Order Line')
    start_date = fields.Date('Date From') #, required=True
    end_date = fields.Date(string="Date To")
    company = fields.Char('Company')
    
    

category_wzd()
 
class CategoryMaster(models.Model):
    _name = "category.masters"
    _description = "category Master"
    
    attribute_id = fields.Many2one('category.wzd',string='attribute_id',ondelete='cascade')
    name = fields.Char(string="Category")
    org_id=fields.Char(string="Organization")
    depart=fields.Char(string="Department Id")
    cate=fields.Char(string="Category Id")
     
           
CategoryMaster()
    
     
  
    
