from odoo import models, fields



class SSDEPTFormView(models.Model):
    _name = 'ss.dept.wise.sales.view'
    _rec_name = 'department'
   
    department = fields.Char(string="Department")
    tax = fields.Float(string="Taxable Amt")
    tax_amt = fields.Float(string="Tax Amt")
    cgst = fields.Float(string="Cgst")
    sgst = fields.Float(string="Sgst")
    cessamt = fields.Float(string="Cessamt")
    mark_down = fields.Float(string="Markdown")
    total = fields.Float(string="Total Amt")
    
    
    def get_data(self): 
        print('function')
        self.env['ss.dept.wise.sales.view'].search([]).unlink()
        fetched_data=self.env['ss.dept.wise.sales.line'].search([])
        if fetched_data:
            print('fetched_data',fetched_data)
     
            for rec in fetched_data:
                print('for',rec)
                self.create({  
                    'department':rec.department,
                    'tax':rec.tax,
                    'tax_amt' :rec.tax_amt,
                    'cgst' :rec.cgst,
                    'sgst':rec.sgst,
                    'cessamt':rec.cessamt,
                    'mark_down':rec.mark_down,
                    'total' :rec.total,                                                             
        })
            
    
            return {
                        'name':  'SuperStore Department Wise Sales Form',
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'ss.dept.wise.sales.view',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current', 
                }
        