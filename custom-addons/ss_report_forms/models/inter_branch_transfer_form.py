from odoo import models, fields



class SSIntrBrchFormView(models.Model):
    _name = 'ss.inter.branch.view'
    
   
    branch = fields.Char(string="Branch") 
    inter_branch = fields.Char(string="Inter Branch") 
    description = fields.Char(string="Description") 
    doc_no = fields.Char(string="Doc No")        
    movement_date = fields.Date('Movement Date')
    code = fields.Integer('Product Code')
    product_name = fields.Char('Product Name')
    transfer_qty = fields.Float('Transfer Quantity')
    mrp = fields.Float('MRP')
    basic_cost = fields.Float('Basic Cost')
    basic_cost_total = fields.Float('Toatl Basic Cost')
    tax = fields.Char('Tax')
    l_cost = fields.Float('Landed Cost')
    l_cost_total = fields.Float('Total Landed Cost')
    department = fields.Char(string="Department")
    category = fields.Char('Category')
    sub_category = fields.Char('Sub Category')
    vendor = fields.Char('Vendor')
    doc_type = fields.Char('Document Type')
  
    def get_data(self): 
        self.env['ss.inter.branch.view'].search([]).unlink()
        fetched_data=self.env['ss.inter.branch.transfer.screen.line'].search([])
        if fetched_data:
            for rec in fetched_data:
                self.create({  
                      
                                'branch':rec.branch ,
                                'inter_branch':rec.inter_branch  ,
                                'description' : rec.description ,
                                'doc_no' : rec.doc_no ,
                                'movement_date' : rec.movement_date ,
                                'code' : rec.code ,
                                'product_name' : rec.product_name ,
                                'transfer_qty' : rec.transfer_qty ,
                                'mrp' : rec.mrp ,
                                'basic_cost' : rec.basic_cost ,
                                'basic_cost_total' : rec.basic_cost_total ,
                                'tax' : rec.tax ,
                                'l_cost' : rec.l_cost ,
                                'l_cost_total' : rec.l_cost_total ,
                                'department' : rec.department ,
                                'category':rec.category ,
                                'sub_category':rec.sub_category,
                                'vendor':rec.vendor,
                                'doc_type':rec.doc_type,                                                      
        })
            
    
            return {
                        'name':  'Inter Branch Transfer Form',
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'ss.inter.branch.view',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current', 
                }
        