from odoo import models, fields



class SSTotSalFormView(models.Model):
    _name = 'ss.total.sales.view'
    _rec_name = 'datetrx'
   
    datetrx = fields.Date(string="Datetrx")
    total_sales_amt = fields.Float(string="Total Sales Amt")
    dis_amt = fields.Float(string="Discount Amt")
    round_off = fields.Float(string="RoundOff")
    tot_net_amt = fields.Float(string="Total Net Amt")
    bill_count = fields.Float(string="Bill Count")
    avg_bill = fields.Float(string="Avg Bill")
  
    def get_data(self):
        self.env['ss.total.sales.view'].search([]).unlink()
        fetched_data=self.env['ss.total.sales.line'].search([])
        if fetched_data:
     
            for rec in fetched_data:
                self.create({  
                      'datetrx':rec.datetrx ,
                                'total_sales_amt':rec.total_sales_amt ,
                                'dis_amt':rec.dis_amt  ,
                                'round_off':rec.round_off ,
                                'tot_net_amt':rec.tot_net_amt,
                                'bill_count':rec.bill_count,
                                'avg_bill':rec.avg_bill,                                                      
        })
            
    
            return {
                        'name':  'Total Sales Form',
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'ss.total.sales.view',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current', 
                }
        