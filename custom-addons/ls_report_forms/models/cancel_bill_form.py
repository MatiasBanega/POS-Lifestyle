from odoo import models, fields



class FormView(models.Model):
    _name = 'cancel.bill.view'
    _rec_name = 'date'
   
    date = fields.Date(string="Date")
    bill_date = fields.Date(string="Bill Date")
    bill_number = fields.Integer(string="Bill No")
    uname = fields.Char(string="User Name")
    pcode = fields.Integer(string="Product Code")
    pname = fields.Char(string="Product Name")
    total_amt = fields.Float(string="Total Amount")
    def get_data(self): 
        print('function')
        self.env['cancel.bill.view'].search([]).unlink()
        fetched_data=self.env['bill.cancel.line'].search([])
        if fetched_data:
            print('fetched_data',fetched_data)
     
            for rec in fetched_data:
                print('for',rec)
                self.create({  
                       'bill_date' : rec.date ,
                                'bill_number' : rec.bill_number ,
                                'uname' : rec.uname ,
                                'pcode' : rec.pcode ,
                                'pname' : rec.pname ,
                                'total_amt' : rec.total_amt ,
                                                                                      
        })
            
    
            return {
                        'name':  'Cancelled Bill Form',
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'cancel.bill.view',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current', 
                }
        