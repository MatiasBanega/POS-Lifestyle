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

class vendor(models.Model):
    _name = "vendor.view"
       
    start_date = fields.Date('Date From') #, required=True
    end_date = fields.Date(string="Date To")
    company=fields.Many2one('res.company',string="Company") #, required=True
   
    def get_vendor(self):
        list=[]
        def get_lines(self):
            res = {}
            dict={}
            lis=[]
            list=[]
            start_date = self.start_date
            end_date = self.end_date
            company=self.company.name
            
            try:
                db_conn = self.env['db.connection'].search([])
                for rec in db_conn:    
                    db_connect=rec.database_connect()
                    list.append(db_connect)
                    cursor = db_connect.cursor() 
                
                    sqls='''
         
                      delete from vendor_master
                       '''
                                       
                    self.env.cr.execute(sqls)
                    
                    sql='''
         
                      select name,ad_org_id as org_id  from c_bpartner
    
                       '''
                                
                    cursor.execute(sql)
                    sale_data = cursor.fetchall()
                    for row in sale_data:                
                        dict = {'name':row[0],'org_id':row[1],}
                        lis.append(dict)
                return lis
                return list
            except (Exception, psycopg2.Error) as error:
                raise UserError(_("Error while fetching data from PostgreSQL "))

            finally:
    # closing database connection.
                if db_conn:
                    cursor.close()
                    db_connect.close()
                    
    
        sum_amt = 0
        tot_amt = 0
        vendor_line = []
        seq = 0
        for line in get_lines(self):
                         
            vendor_line.append((0,0,{
                                'name' : line['name'],
                                'org_id' : line['org_id'],
                                
                                     }))
        if vendor_line:
            vendor_line.append((0,0,{
                                }))    
                            
         
        vals = {
                 'vendor_line': vendor_line,
                        
                }
        vendor_id = self.env['vendor.wzd'].create(vals)

        res = self.env['ir.model.data'].check_object_reference(
                                            'lifestyle_masters', 'vendor_wizard')
        return {
                    'name': '',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'vendor.wzd',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                     'res_id': vendor_id.id,
            }
       
class Vendor_wzd(models.Model):
    _name = "vendor.wzd"
    _description = "Vendor Wizard"
    
    
    name = fields.Char(default="Vendor Wizard")
    vendor_line = fields.One2many('vendor.master','attribute_id',string='Open Order Line')
    start_date = fields.Date('Date From') #, required=True
    end_date = fields.Date(string="Date To")
    company = fields.Char('Company')
    

Vendor_wzd()
 
class VendorMaster(models.Model):
    _name = "vendor.master"
    _description = "Vendor Master"
    
    attribute_id = fields.Many2one('vendor.wzd',string='attribute_id',ondelete='cascade')
    name = fields.Char(string="Vendor")
    org_id=fields.Char(string="Organization")
    
     
           
VendorMaster()
    
     
  
    
