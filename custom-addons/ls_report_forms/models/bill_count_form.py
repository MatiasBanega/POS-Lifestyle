from odoo import models, fields



class FormView(models.Model):
    _name = 'bill.count.view'
    _rec_name = 'terminal'
    
    
    terminal = fields.Char(string="Terminal")
    startno = fields.Integer(string="Startno")
    endno = fields.Integer(string="Endno")
    totalbillcount = fields.Integer("Total Bill Count")
    oflinecnt = fields.Integer(string="Offline Count")
    onlinecnt = fields.Integer(string="Online Count")
    cancelcount = fields.Integer(string="Cancel Count")
    def get_data(self): 
        print('function')
        self.env['bill.count.view'].search([]).unlink()
        fetched_data=self.env['billno.count.line'].search([])
        if fetched_data:
            print('fetched_data',fetched_data)
     
            for rec in fetched_data:
                print('for',rec)
                self.create({  
                     'terminal' : rec.terminal ,
                                'startno' : rec.startno ,
                                'endno' : rec.endno ,
                                'totalbillcount' : rec.totalbillcount ,
                                'onlinecnt' : rec.onlinecnt ,
                                'oflinecnt' : rec.oflinecnt ,
                                'cancelcount' : rec.cancelcount ,
                           
                                                                                      
        })
            
    
            return {
                        'name':  'Bill Count Form',
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'bill.count.view',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current', 
                }
        