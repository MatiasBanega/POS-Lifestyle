from odoo import models, fields, api, _



class SSSummaryFormView(models.Model):
    _name = 'ss.summary.sales.view'
    _rec_name = 'pos'
   
    date = fields.Date('Date')
    pos = fields.Char('POS') 
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
    cashdisc = fields.Float('cashdisc')
    cr_sal = fields.Float('cr_sal')
    cr_disc = fields.Float('cr_disc')
    cashinhand = fields.Float('cashinhand')
    ex_sh = fields.Float('ex_sh')
    bills = fields.Float('bills')
    
    
    def get_data(self): 
        print('function')
        self.env['ss.summary.sales.view'].search([]).unlink()
        
        fetched_data=self.env['summary.sales.report.screen.line.ss'].search([])
        print('fetched_data',fetched_data)
#         sqls='''
#            
#                     delete from form_view
#                        '''
#         self.env.cr.execute(sqls)
#         print('sqls',sqls)
        
        for rec in fetched_data:

            print('for',rec)
            self.create({   'date' : rec.date,
                                    'pos' : rec.pos, 
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
                                    'cashdisc' : rec.cashdisc ,
                                    'cr_sal' : rec.cr_sal,
                                    'cr_disc' : rec.cr_disc,
                                    'cashinhand': rec.cashinhand,
                                    'ex_sh' : rec.ex_sh,
                                    'bills': rec.bills,
          
                                                                       
                                                                  
                                                                  
    })
        

#         res = self.env['ir.model.data'].check_object_reference(
#                                             'form_view', 'form_view')
        return {
                    'name': 'Summary Sales Report',
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'ss.summary.sales.view',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
#                      'res_id': vendor_id.id,
            }
    