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
#                 db_conn = self.env['db.connection'].search([('company_id','=',self.company.id)], limit=1)
                print('db_conn',db_conn.company_id,self.company) 
                print('db_conn',db_conn) 
                for rec in db_conn: 
                    print('rec',rec)     
                    db_connect=rec.database_connect()
                    cursor = db_connect.cursor() 
                
                    sqls='''
         
                      delete from department_master
                       '''
                         
                                      
        #             if start_date and end_date:
        #                 sql += "where pos.date_order between '%s' and '%s'" % (start_date, end_date)
        #             if product_id:
        #                 sql +=" and pt.name ='%s'"%(product_id)                  
                    self.env.cr.execute(sqls)
                    print('sqls',sqls)
                    
                    sql='''
         
                      select name,ad_org_id as org_id from um_product_department
    
                       '''
                         
                                      
        #             if start_date and end_date:
        #                 sql += "where pos.date_order between '%s' and '%s'" % (start_date, end_date)
        #             if product_id:
        #                 sql +=" and pt.name ='%s'"%(product_id)                  
                    cursor.execute(sql)
                    print(sql)
                    sale_data = cursor.fetchall()
                    print('sale_data',sale_data)
                    for row in sale_data:                
                        dict = {'name':row[0],'org_id':row[1],}
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
                    
    
        sum_amt = 0
        tot_amt = 0
        department_line = []
        seq = 0
        for line in get_lines(self):
                         
            department_line.append((0,0,{
                                'name' : line['name'],
                                'org_id' : line['org_id'],
#                                 'Date Invoiced' : line['Date Invoiced'],
#                                 'Process Instance' : line['Process Instance'],
#                                 'Sales Attribute' : line['Sales Attribute'], 
#                                 'Sold Qty' : line['Sold Qty'],
#                                 'Sold value' : line['Sold value']
                                
                                     }))
        if department_line:
            department_line.append((0,0,{
#                                     'date' : False,
#                                     'department' :False, 
#                                     'paymode' : False,
#                                     'total' : False
                                }))    
                            
         
        vals = {
                #'name': 'Beat outstanding Report',
                #'end_date_title':'AS ON DATE: ',             
                #'partner_id': self.partner_id.name,
#                  'customer_type_title':'TYPE: ',             
#                  'customer_type': self.customer_type,
                 'department_line': department_line,
                #'visible':True,            
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
    
     
           
DepartmentMaster()
    
     
  
    