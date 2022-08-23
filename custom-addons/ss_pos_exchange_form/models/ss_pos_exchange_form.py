from odoo import models, fields



class FormView(models.Model):
    _name = 'ss.pos.product.wise.exchange.view'
    _rec_name = 'product_name'
    
    exchange_bill = fields.Char(string="Exchangebill")
    original_bill = fields.Char(string="Originalbill")
    invoice_date = fields.Date(string="Invoicedate")
    product_code = fields.Integer(string="Productcode")
    product_name = fields.Char(string="Productname")
    
    return_qty = fields.Integer(string="Returnqty")
    original_invoicesp = fields.Char(string="Originalinvoicesp")
    line_total = fields.Float(string="Linetotal")
#     balance_amt = fields.Float(string="Balanceamt")
    cashier = fields.Char(string="Cashier")
    terminal = fields.Char(string="Terminal")
#     sales_rep = fields.Char(string="Salesrep")
    
    def get_data(self): 
        print('function')
        self.env['ss.pos.product.wise.exchange.view'].search([]).unlink()
        fetched_data=self.env['ss.pos.exchange.product.screen.line'].search([])
        if fetched_data:
            print('fetched_data',fetched_data)
     
            for rec in fetched_data:
                print('for',rec)
                self.create({  
                     'exchange_bill' : rec.exchange_bill ,
                                'original_bill' : rec.original_bill ,
                                'invoice_date' : rec.invoice_date ,
                                'product_code' : rec.product_code ,
                                'product_name' : rec.product_name ,
                                
                                'return_qty' : rec.return_qty ,
                                'original_invoicesp' : rec.original_invoicesp ,
                                'line_total' : rec.line_total ,
#                                 'balance_amt' : rec.balance_amt ,
                                'cashier' : rec.cashier ,
                                'terminal' : rec.terminal ,
                                                                                
        })
            
    
            return {
                        'name':  'POS Product Wise Exchange Form ',
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'ss.pos.product.wise.exchange.view',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current', 
                }
        