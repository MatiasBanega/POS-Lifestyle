from odoo import api,models,fields

#Parent class
class SSPos_Reports(models.Model):
    _name = "superstore.reports"
    _description ="SuperStore Report"
    
    name =  fields.Char(string="Name")
    
   