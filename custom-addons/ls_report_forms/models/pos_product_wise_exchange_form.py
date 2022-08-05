from odoo import models, fields



class FormView(models.Model):
    _name = 'pos.product.wise.exchange.view'
    _rec_name = 'product_name'
    
    exchange_bill = fields.Char(string="Exchangebill")
    original_bill = fields.Char(string="Originalbill")
    invoice_date = fields.Date(string="Invoicedate")
    product_code = fields.Integer(string="Productcode")
    product_name = fields.Char(string="Productname")
    brand = fields.Char(string="Brand")
    item_type = fields.Char(string="Itemtype")
    product_design = fields.Char(string="Productdesign")
    product_color = fields.Char(string="Productcolor")
    product_size = fields.Char(string="Productsize")
    exchange_qty = fields.Integer(string="Exchangeqty")
    original_billsp = fields.Char(string="Originalbillsp")
    line_total = fields.Float(string="Linetotal")
    balance_amt = fields.Float(string="Balanceamt")
    cashier = fields.Char(string="Cashier")
    terminal = fields.Char(string="Terminal")
    sales_rep = fields.Char(string="Salesrep")
    
    def get_data(self): 
        print('function')
        self.env['pos.product.wise.exchange.view'].search([]).unlink()
        fetched_data=self.env['pos.exchange.product.screen.line'].search([])
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
                                'brand' : rec.brand ,
                                'item_type' :rec.item_type ,
                                'product_design' : rec.product_design ,
                                'product_color' : rec.product_color ,
                                'product_size' : rec.product_size ,
                                'exchange_qty' : rec.exchange_qty ,
                                'original_billsp' : rec.original_billsp ,
                                'line_total' : rec.line_total ,
                                'balance_amt' : rec.balance_amt ,
                                'cashier' : rec.cashier ,
                                'terminal' : rec.terminal ,
                                'sales_rep' : rec.sales_rep ,
                                                                                
        })
            
    
            return {
                        'name':  'POS Product Wise Exchange Form ',
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'pos.product.wise.exchange.view',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current', 
                }
        