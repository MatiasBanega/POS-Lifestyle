from odoo import models, fields



class FormView(models.Model):
    _name = 'cashier.wise.sales.view'
    _rec_name = 'date'
   
    date = fields.Date(string="Date")
    name = fields.Char(string="Name")
    tender_type = fields.Char(string="Tender Type")
    amt = fields.Float(string="Amount")
  
    def get_data(self): 

        self.env['cashier.wise.sales.view'].search([]).unlink()
        fetched_data=self.env['cashier.sales.report.screen.line'].search([])
        if fetched_data:

     
            for rec in fetched_data:

                self.create({  
                       'date' :rec.date,
                                'name' :rec.name,
                                'tender_type' :rec.tender_type,
                                'amt' :rec.amt,                                                  
        })
            
    
            return {
                        'name':  'Cashier Wise Sales Report',
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'cashier.wise.sales.view',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current', 
                }
        