from odoo import models, fields



class Stock_Adjust_FormView(models.Model):
    _name = 'stock.adjustment.form.view'
    _rec_name = 'ls_date'
   
    ls_date = fields.Date(string="Date")
    
    ls_branch = fields.Char(string="Branch")
    ls_description = fields.Char(string="Description")
    ls_doc_number = fields.Char(string="Document Number")
    ls_s_date = fields.Date(string="Start Date")
    ls_code = fields.Integer(string="Code")
    ls_pdt_name = fields.Char(string="Product Name")
    ls_brand = fields.Char(string="Brand")
    ls_itemtype = fields.Char(string="Item Type")
    ls_pdt_design = fields.Char(string="Product Design")
    ls_pdt_color = fields.Char(string="Product Color")
    ls_pdt_size = fields.Char(string="Product Size")
    ls_adjustment_qty = fields.Float(string="Adjustment Qty")
    ls_mrp_rate = fields.Float(string="MRP")
    ls_l_cost = fields.Float(string="L Cost")
    ls_l_cost_total = fields.Float(string="L Cost Total")
    ls_fgc = fields.Float(string="FGC")
    ls_fgc_total = fields.Float(string="FGC Total")
    ls_tax_total = fields.Float(string="Tax Total")
    ls_depart_ment = fields.Char(string="Department")
    ls_category = fields.Char(string="Category")
    ls_sub_category = fields.Char(string="Sub Category")
    ls_vendor = fields.Char(string="Vendor")
    ls_doc_type = fields.Char(string="Document Type")
    ls_sub_doc_type = fields.Char(string="Sub Document Type")
    ls_inv_sub_type = fields.Char(string="Inv Sub Type")
      
  
      
  
    def get_data(self): 
        print('function')
        self.env['stock.adjustment.form.view'].search([]).unlink()
        fetched_data=self.env['stock.adjustment.line'].search([])
        if fetched_data:
            print('fetched_data',fetched_data)
     
            for rec in fetched_data:
                print('for',rec)
                self.create({  
                        'ls_branch' : rec.branch ,
                        'ls_description' : rec.description ,
                        'ls_doc_number' : rec.doc_number ,
                        'ls_s_date' : rec.s_date ,
                        'ls_code' : rec.code ,
                        'ls_pdt_name' : rec.pdt_name ,
                        'ls_brand' : rec.brand ,
                        'ls_itemtype' : rec.itemtype ,
                        'ls_pdt_design' : rec.pdt_design ,
                        'ls_pdt_color' : rec.pdt_color ,
                        'ls_pdt_size' : rec.pdt_size ,
                        'ls_adjustment_qty' : rec.adjustment_qty ,
                        'ls_mrp_rate' : rec.mrp_rate ,
                        'ls_l_cost' : rec.l_cost ,
                        'ls_l_cost_total' : rec.l_cost_total ,
                        'ls_fgc' : rec.fgc ,
                        'ls_fgc_total' : rec.fgc_total ,
                        'ls_tax_total' : rec.tax_total ,
                        'ls_depart_ment' : rec.depart_ment ,
                        'ls_category' : rec.category ,
                        'ls_sub_category' : rec.sub_category ,
                        'ls_vendor' : rec.vendor ,
                        'ls_doc_type' : rec.doc_type ,
                        'ls_sub_doc_type' : rec.sub_doc_type ,
                        'ls_inv_sub_type' : rec.inv_sub_type ,
                                                                                      
        })
            
    
            return {
                        'name':  'Stock Adjustment Form',
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'stock.adjustment.form.view',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current', 
                }
        