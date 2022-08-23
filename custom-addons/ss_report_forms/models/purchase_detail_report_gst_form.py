from odoo import models, fields



class SSPurchaseFormView(models.Model):
    _name = 'ss.purchase.detail.report.gst.view'
    _rec_name = 'grn_no'
   
    grn_no = fields.Char(string="GRN No")
    bill_no = fields.Char(string="Bill No")
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
    
    