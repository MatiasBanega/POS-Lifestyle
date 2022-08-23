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

class organization(models.Model):
    _name = "organization.view"
       
    start_date = fields.Date('Date From') #, required=True
    end_date = fields.Date(string="Date To")
    company=fields.Many2one('res.company',string="Company") #, required=True
   
    def get_organization(self):
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
         
                      delete from organization_master
                       '''
                                      
                    self.env.cr.execute(sqls)
                    
                    sql='''
         
                      select name,ad_org_id as org_id from ad_org
    
                       '''
                         
                                     
                    cursor.execute(sql)
                    sale_data = cursor.fetchall()
                    for row in sale_data:                
                        dict = {'name':row[0],'org_id':row[1],}
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
        organization_line = []
        seq = 0
        for line in get_lines(self):
                         
            organization_line.append((0,0,{
                                'name' : line['name'],
                                'org_id' : line['org_id'],
                                
                                     }))
        if organization_line:
            organization_line.append((0,0,{
                                }))    
                            
         
        vals = {
                 'organization_line': organization_line,
                      
                }
        organization_id = self.env['organization.wzd'].create(vals)

        res = self.env['ir.model.data'].check_object_reference(
                                            'lifestyle_masters', 'organization_wizard')
        return {
                    'name': '',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'organization.wzd',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                     'res_id': organization_id.id,
            }
       
class organization_wzd(models.Model):
    _name = "organization.wzd"
    _description = "Organization Wizard"
    
    
    name = fields.Char(default="Organization Wizard")
    organization_line = fields.One2many('organization.master','attribute_id',string='Open Order Line')
    start_date = fields.Date('Date From') #, required=True
    end_date = fields.Date(string="Date To")
    company = fields.Char('Company')
    

organization_wzd()
 
class OrganizationMaster(models.Model):
    _name = "organization.master"
    _description = "Organization Master"
    
    attribute_id = fields.Many2one('organization.wzd',string='attribute_id',ondelete='cascade')
    name = fields.Char(string="Organization")
    org_id=fields.Char(string="Org ID")
    
     
           
OrganizationMaster()
    
     
  
    
