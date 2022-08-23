from odoo import models, fields



class FormView(models.Model):
    _name = 'inter.branch.report.form.view'
    _rec_name = 'branch'
   
    branch = fields.Char(string="Branch") 
    inter_branch = fields.Char(string="Inter Branch") 
    description = fields.Char(string="Description") 
    doc_no = fields.Char(string="Doc No")        
    movement_date = fields.Date('Movement Date')
    code = fields.Integer()
    product_name = fields.Char()
    brand = fields.Char()
    product_design = fields.Char()
    item_type = fields.Char()
    product_color = fields.Char()
    product_size = fields.Char()
    transfer_qty = fields.Float()
    mrp = fields.Float()
    basic_cost = fields.Float()
    basic_cost_total = fields.Float()
    tax = fields.Char()
    l_cost = fields.Float()
    l_cost_total = fields.Float()
    department = fields.Char(string="Department")
    category = fields.Char()
    sub_category = fields.Char()
    vendor = fields.Char()
    doc_type = fields.Char()
  
    def get_data(self): 

        self.env['inter.branch.report.form.view'].search([]).unlink()
        fetched_data=self.env['inter.branch.transfer.screen.line'].search([])
        if fetched_data:

            for rec in fetched_data:

                self.create({  
                            'branch' : rec.branch,
                            'inter_branch' : rec.inter_branch,
                            'description' : rec.description,
                            'doc_no' : rec.doc_no,
                            'movement_date' : rec.movement_date,
                            'code' : rec.code,
                            'product_name' : rec.product_name,
                            'brand' : rec.brand,
                            'product_design' : rec.product_design,
                            'item_type' : rec.item_type,
                            'product_color' : rec.product_color,
                            'product_size' : rec.product_size,
                            'transfer_qty' : rec.transfer_qty,
                            'mrp' : rec.mrp,
                            'basic_cost' : rec.basic_cost,
                            'basic_cost_total' : rec.basic_cost_total,
                            'tax' : rec.tax,
                            'l_cost' : rec.l_cost,
                            'l_cost_total' : rec.l_cost_total,
                            'department' : rec.department,
                            'category' : rec.category,
                            'sub_category' : rec.sub_category,
                            'vendor' : rec.vendor,
                            'doc_type' : rec.doc_type, 
                        })
            
    
            return {
                        'name':  'Total Sales Form',
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'inter.branch.report.form.view',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current', 
                }