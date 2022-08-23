from odoo import models, fields



class FormView(models.Model):
    _name = 'purchase.detail.report.gst.view'
    _rec_name = 'grn_no'
   
    grn_no = fields.Char(string="GRN No")
    bill_no = fields.Char(string="Bill No")
    bill_date = fields.Date(string="Bill Date")
    grn_date = fields.Date(string="GRN Date")
    partner_id = fields.Char(string="Vendor")
    ware_house = fields.Char(string="Warehouse")
    sub_total = fields.Float(string="SubTotal")
    tax_amt = fields.Float(string="Tax Amount")
    cess = fields.Float(string="CESS")
    total_val = fields.Float(string="Total Value")
    add_ded = fields.Float(string="Add Ded")
    tcs_amt = fields.Float(string="Tcs Amount")
    net_amt = fields.Float(string="Net Amount")
    freight_charges = fields.Float(string="Freight Charges")
    pcode = fields.Char(string="Pcode")
    product_id = fields.Char(string="Product Name")
    brand = fields.Char(string="Brand")
    item_type = fields.Char(string="Item Type")
    prod_design = fields.Char(string="Product Design")
    prod_color = fields.Char(string="Product Color")
    prod_size = fields.Char(string="Product Size")
    qty = fields.Float(string="Quantity")
    mrp = fields.Float(string="MRP")
    gkm = fields.Float(string="GKM")
    sp_margin_mrp = fields.Float(string="Selling Margin MRP")
    m_down = fields.Float(string="Mark Down")
    diff_margin = fields.Float(string="Different Margin")
    diff_amt = fields.Float(string="Different Amount")
    lcost = fields.Float(string="Landed Cost")
    line_subtot = fields.Float(string="Line SubTotal")
    dept = fields.Char(string="Department")
    categ = fields.Char(string="Category")
    manuftr = fields.Char(string="Manufacturer")
    tax = fields.Char(string="Tax")
    igst = fields.Float(string="IGST")
    cgst = fields.Float(string="CGST")
    sgst = fields.Float(string="SGST")
    line_taxtot = fields.Float(string="Line Taxtotal")
    cess_tot = fields.Float(string="CESS Total")
    created = fields.Char(string="Created")
    reversal_no = fields.Char(string="Reversal No")
    reversed_date = fields.Date(string="Reversed Date")
    
    def get_data(self): 
        self.env['purchase.detail.report.gst.view'].search([]).unlink()
        fetched_data=self.env['purchase.detail.report.screen.line'].search([])
        if fetched_data:
     
            for rec in fetched_data:
                self.create({  
                        'grn_no' : rec.grn_no ,
                                'bill_no' : rec.bill_no ,
                                'bill_date' : rec.bill_date ,
                                'grn_date' : rec.grn_date ,
                                'partner_id' : rec.partner_id ,
                                'ware_house' : rec.ware_house ,
                                'sub_total' : rec.sub_total ,
                                'tax_amt' : rec.tax_amt ,
                                'cess' : rec.cess ,
                                'total_val' : rec.total_val ,
                                'add_ded' : rec.add_ded ,
                                'tcs_amt' : rec.tcs_amt ,
                                'net_amt' : rec.net_amt ,
                                'freight_charges' : rec.freight_charges ,
                                'pcode' : rec.pcode ,
                                'product_id' : rec.product_id ,
                                'brand' : rec.brand ,
                                'item_type' : rec.item_type ,
                                'prod_design' : rec.prod_design ,
                                'prod_color' : rec.prod_color ,
                                'prod_size' : rec.prod_size ,
                                'qty' : rec.qty ,
                                'mrp' : rec.mrp ,
                                'gkm' : rec.gkm ,
                                'sp_margin_mrp' : rec.sp_margin_mrp ,
                                'm_down' : rec.m_down ,
                                'diff_margin' : rec.diff_margin ,
                                'diff_amt' : rec.diff_amt ,
                                'lcost' : rec.lcost ,
                                'line_subtot' : rec.line_subtot ,
                                'brand' : rec.brand ,
                                'dept' : rec.dept ,
                                'categ' : rec.categ ,
                                'manuftr' : rec.manuftr ,
                                'tax' : rec.tax ,
                                'igst' : rec.igst ,
                                'cgst' : rec.cgst ,
                                'sgst' : rec.sgst ,
                                'line_taxtot' : rec.line_taxtot ,
                                'cess_tot' : rec.cess_tot ,
                                'created' : rec.created ,
                                'reversal_no' : rec.reversal_no ,
                                'reversed_date' : rec.reversed_date ,
                                                                                
        })
            
    
            return {
                        'name':  'Purchase Detail Report with GST Form',
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'purchase.detail.report.gst.view',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current', 
                }
        