from odoo import models, fields, api, _
import psycopg2
         
class DBCONNECTION(models.Model):
    _name = 'db.connection'
    _inherit = ['mail.thread']
    _description = 'Database Connection'
    _order = 'id desc'  
    
 #all fields are required to connect external db    
    name = fields.Char(string='Username', required=True,store=True,tracking=True)    
    company_id = fields.Many2one('res.company',string="Company",store=True,tracking=True)
    password = fields.Char(string="Password",store=True,required=True,tracking=True)
    host = fields.Char(string="Host", required=True,store=True,tracking=True)
    port = fields.Char(string='Port', required=True,store=True,tracking=True)
    data_base = fields.Char(string="Database" ,required=True,store=True,tracking=True)

## Unique Company     
    _sql_constraints = [
        ('company_uniq', 'unique (company_id)', 'Company Must Be Unique !')
    ]
 #To get values for the above fields 
    def database_connect(self):
        return psycopg2.connect(user=self.name,
                                  password=self.password,
                                  host=self.host,
                                  port=self.port,
                                  database=self.data_base)
            
        
            
             
    
    
    