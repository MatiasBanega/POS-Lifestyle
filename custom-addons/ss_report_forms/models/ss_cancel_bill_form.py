from odoo import models, fields



class SS_Cancel_FormView(models.Model):
    _name = 'ss.cancel.bill.view'
    _rec_name = 'date_ss'
   
    date_ss = fields.Date(string="Date")
    bill_ss_date = fields.Date(string="Bill Date")
    bill_ss_number = fields.Integer(string="Bill No")
    uname_ss = fields.Char(string="User Name")
    pcode_ss = fields.Integer(string="Product Code")
    pname_ss = fields.Char(string="Product Name")
    total_ss_amt = fields.Float(string="Total Amount")
    
    def get_data(self): 
        self.env['ss.cancel.bill.view'].search([]).unlink()
        fetched_data=self.env['ss.bill.cancel.line'].search([])
        if fetched_data:
     
            for rec in fetched_data:
                self.create({  
                       'bill_ss_date' : rec.ss_date ,
                                'bill_ss_number' : rec.ss_bill_number ,
                                'uname_ss' : rec.ss_uname ,
                                'pcode_ss' : rec.ss_pcode ,
                                'pname_ss' : rec.ss_pname ,
                                'total_ss_amt' : rec.ss_total_amt ,
                                                                                      
        })
            
    
            return {
                        'name':  'Cancelled Bill Form',
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'ss.cancel.bill.view',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current', 
                }
        