from odoo import models, fields



class SS_Stock_Adjust_FormView(models.Model):
    _name = 'ss.stock.adjustment.form.view'
    _rec_name = 'date_s'
   
    date_s = fields.Date(string="Date")
    branch_ss = fields.Char(string="Branch")
    description_ss = fields.Char(string="Description")
    doc_number_ss = fields.Char(string="Document Number")
    date_ss = fields.Date(string="Start Date")
    code_ss = fields.Integer(string="Code")
    pdt_name_ss = fields.Char(string="Product Name")   
    adjustment_qty_ss = fields.Float(string="Adjustment Qty")
    mrp_rate_ss = fields.Float(string="MRP")
    l_cost_ss = fields.Float(string="L Cost")
    l_cost_total_ss = fields.Float(string="L Cost Total")
    fgc_ss = fields.Float(string="FGC")
    fgc_total_ss = fields.Float(string="FGC Total")
    tax_total_ss = fields.Float(string="Tax Total")
    depart_ment_ss = fields.Char(string="Department")
    category_ss = fields.Char(string="Category")
    sub_category_ss = fields.Char(string="Sub Category")
    brand_ss = fields.Char(string="Brand")
    vendor_ss = fields.Char(string="Vendor")
    doc_type_ss = fields.Char(string="Document Type")
    sub_doc_type_ss = fields.Char(string="Sub Document Type")
    inv_sub_type_ss = fields.Char(string="Inv Sub Type")
      
  
    def get_data(self): 
        print('function')
        self.env['ss.stock.adjustment.form.view'].search([]).unlink()
        fetched_data=self.env['super.stock.adjustment.line'].search([])
        if fetched_data:
            print('fetched_data',fetched_data)
     
            for rec in fetched_data:
                print('for',rec)
                self.create({  
                       'branch_ss' : rec.ss_branch ,
                                'description_ss' : rec.ss_description ,
                                'doc_number_ss' : rec.ss_doc_number ,
                                'date_ss' : rec.ss_date ,
                                'code_ss' : rec.ss_code ,
                                'pdt_name_ss' : rec.ss_pdt_name ,
                                'adjustment_qty_ss' : rec.ss_adjustment_qty ,
                                'mrp_rate_ss' : rec.ss_mrp_rate ,
                                'l_cost_ss' : rec.ss_l_cost ,
                                'l_cost_total_ss' : rec.ss_l_cost_total ,
                                'fgc_ss' : rec.ss_fgc ,
                                'fgc_total_ss' : rec.ss_fgc_total ,
                                'tax_total_ss' : rec.ss_tax_total ,
                                'depart_ment_ss' : rec.ss_depart_ment ,
                                'category_ss' : rec.ss_category ,
                                'sub_category_ss' : rec.ss_sub_category ,
                                'brand_ss' : rec.ss_brand ,
                                'vendor_ss' : rec.ss_vendor ,
                                'doc_type_ss' : rec.ss_doc_type ,
                                'sub_doc_type_ss' : rec.ss_sub_doc_type ,
                                'inv_sub_type_ss' : rec.ss_inv_sub_type ,
                                                                                      
        })
            
    
            return {
                        'name':  'Stock Adjustment  Form',
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'ss.stock.adjustment.form.view',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current', 
                }
        