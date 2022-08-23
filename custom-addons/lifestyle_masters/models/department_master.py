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

class Department(models.Model):
    _name = "department.view"
       
    start_date = fields.Date('Date From') #, required=True
    end_date = fields.Date(string="Date To")
    company=fields.Many2one('res.company',string="Company") #, required=True
   
    def get_department(self):

        def get_lines(self):
            res = {}
            dict={}
            lis=[]
            start_date = self.start_date
            end_date = self.end_date
            company=self.company.name
            
            try:
                db_conn = self.env['db.connection'].search([])
               
                for rec in db_conn: 
                    db_connect=rec.database_connect()
                    cursor = db_connect.cursor() 
                
                    sqls='''
         
                      delete from department_master
                       '''
                         
                                      
                    self.env.cr.execute(sqls)
                    
                    
                    sql='''
         
                      select name,ad_org_id as org_id,um_product_department_id as dep_id from um_product_department
    
                       '''
                                      
                    cursor.execute(sql)
                    
                    sale_data = cursor.fetchall()
                    
                    for row in sale_data:                
                        dict = {'name':row[0],'org_id':row[1],'dep_id':row[2],}
                        
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
        department_line = []
        seq = 0
        for line in get_lines(self):
                         
            department_line.append((0,0,{
                                'name' : line['name'],
                                'org_id' : line['org_id'],
                                'depart_ment_id' : line['dep_id']
                                     }))
        if department_line:
            department_line.append((0,0,{
                                }))    
                            
         
        vals = {
                 'department_line': department_line,
                        
                }
        department_id = self.env['department.wzd'].create(vals)

        res = self.env['ir.model.data'].check_object_reference(
                                            'lifestyle_masters', 'department_wizard')
        return {
                    'name': '',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'department.wzd',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                     'res_id': department_id.id,
            }
       
class department_wzd(models.Model):
    _name = "department.wzd"
    _description = "Department Wizard"
    
    
    name = fields.Char(default="Department Wizard")
    department_line = fields.One2many('department.master','attribute_id',string='Open Order Line')
    start_date = fields.Date('Date From') #, required=True
    end_date = fields.Date(string="Date To")
    company = fields.Char('Company')
    

department_wzd()
 
class DepartmentMaster(models.Model):
    _name = "department.master"
    _description = "department Master"
    
    attribute_id = fields.Many2one('department.wzd',string='attribute_id',ondelete='cascade')
    name = fields.Char(string="Department")
    org_id=fields.Char(string="Organization")
    depart_ment_id=fields.Char(string='Department Id')
    
     
           
DepartmentMaster()
    
     
  
    
