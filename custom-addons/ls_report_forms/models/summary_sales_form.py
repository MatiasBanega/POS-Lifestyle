from odoo import models, fields, api, _



class FormView(models.Model):
    _name = 'summary.sales.view'
    _rec_name = 'pos'
   
    date = fields.Date('Date')
    pos = fields.Char('POS')
    cashier = fields.Char('cashier')
    sale_amount = fields.Float('Sales Amount')
    cash = fields.Float('Cash')
    ccard = fields.Float('ccard')
    voucher = fields.Float('Voucher')
    sodexo = fields.Float('sodexo')
    gift = fields.Float('gift')
    lrvvoc = fields.Float('lrvvoc')
    phonepe = fields.Float('Phonepe')
    googlepay = fields.Float('Google Pay')
    loycoupon = fields.Float('loycoupon')
    parkingtkn = fields.Float('parkingtkn')
    giftpass = fields.Float('Giftpass')
    paytm = fields.Float('Paytm')
    othercpn = fields.Float('othercpn')
    ticket = fields.Float('Ticket')
    txpress = fields.Float('txpress')
    upipayment = fields.Float('upipayment')
    razorpay = fields.Float('razorpay')
    advpaid = fields.Char('advpaid')
    cashdisc = fields.Float('cashdisc')
    cr_sal = fields.Float('cr_sal')
    cr_disc = fields.Float('cr_disc')
    cashinhand = fields.Float('cashinhand')
    ex_sh = fields.Float('ex_sh')
    bills = fields.Float('bills')
    
    
    def get_data(self):
        self.env['summary.sales.view'].search([]).unlink()
        
        fetched_data=self.env['sales.summary.screen.line'].search([])
        
        for rec in fetched_data:
            self.create({   'date' : rec.date,
                                    'pos' : rec.pos,
                                    'cashier' :rec.cashier,
                                    'sale_amount' :rec.sale_amount,
                                    'cash' : rec.cash,
                                    'ccard' :rec.ccard,
                                    'voucher' :rec.voucher,
                                    'sodexo' : rec.sodexo,
                                    'gift' : rec.gift,
                                    'lrvvoc': rec.lrvvoc,
                                    'phonepe' : rec.phonepe,
                                    'googlepay' :rec.googlepay,
                                    'loycoupon' :rec.loycoupon,
                                    'parkingtkn' : rec.parkingtkn,
                                    'giftpass' : rec.giftpass,
                                    'paytm': rec.paytm,
                                    'othercpn': rec.othercpn,
                                    'ticket' : rec.ticket,
                                    'txpress' : rec.txpress,
                                    'upipayment' : rec.upipayment,
                                    'razorpay' : rec.razorpay,
                                    'advpaid': rec.advpaid,
                                    'cashdisc' : rec.cashdisc ,
                                    'cr_sal' : rec.cr_sal,
                                    'cr_disc' : rec.cr_disc,
                                    'cashinhand': rec.cashinhand,
                                    'ex_sh' : rec.ex_sh,
                                    'bills': rec.bills,
          
                                                                       
                                                                  
                                                                  
    })
        

        return {
                    'name': 'Summary Sales Form',
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'summary.sales.view',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
            }
    