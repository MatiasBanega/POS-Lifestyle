from odoo import api,models,fields

#Parent class
class Pos_Reports(models.Model):
    _name = "lifestyle.reports"
    _description ="Detail Report"
    
    name =  fields.Char(string="Name")
    
   