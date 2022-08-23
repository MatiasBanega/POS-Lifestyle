# -*- coding: utf-8 -*-
 
from datetime import datetime, timedelta
 
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

 
class PurchaseDetailsReportGst(models.AbstractModel):    
    _name = 'report.ls_pos_reports.report_purchase_detail_wise'
 
    #@api.model
    def _get_report_values(self, docids, data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        company_id = data['form']['company_id']    

        
        sql = ''' 
      select grn_no,bill_no, bill_date,grn_date, partner_id, ware_house, sub_total,
        tax_amt,cess, total_val, add_ded, tcs_amt,net_amt,freight_charges, pcode, product_id,brand,item_type,
        prod_design,prod_color,prod_size,qty,mrp,gkm,sp_margin_mrp,
        m_down,diff_margin,diff_amt,lcost,line_subtot,dept,categ,manuftr,tax,igst,cgst,sgst,line_taxtot,
        cess_tot,created,reversal_no,reversed_date from purchase_detail_report_screen_line
                where purchase_order_id=(select max(purchase_order_id) from purchase_detail_report_screen_line)    
                
                              
             '''

        self.env.cr.execute(sql)
        emp_data = self.env.cr.dictfetchall()
        docs = []
        seq = 0
        for line in emp_data:
            seq += 1
            today = fields.Date.today()
            todaydate = fields.Date.from_string(today)
            daysdue = ''
            docs.append({
                        'grn_no' : line['grn_no'],
                        'bill_no' : line['bill_no'],
                                'bill_date' : line['bill_date'],
                                'grn_date' : line['grn_date'],
                                'partner_id' : line['partner_id'],
                                'ware_house' : line['ware_house'],
                                'sub_total' : line['sub_total'],
                                'tax_amt' : line['tax_amt'],
                                'cess' : line['cess'],
                                'total_val' : line['total_val'],
                                'add_ded' : line['add_ded'],
                                'tcs_amt' : line['tcs_amt'],
                                'net_amt' : line['net_amt'],
                                'freight_charges' : line['freight_charges'],
                                'pcode' : line['pcode'],
                                'product_id' : line['product_id'],
                                'brand' : line['brand'],
                                'item_type' : line['item_type'],
                                'prod_design' : line['prod_design'],
                                'prod_color' : line['prod_color'],
                                'prod_size' : line['prod_size'],
                                'qty' : line['qty'],
                                'mrp' : line['mrp'],
                                'gkm' : line['gkm'],
                                'sp_margin_mrp' : line['sp_margin_mrp'],
                                'm_down' : line['m_down'],
                                'diff_margin' : line['diff_margin'],
                                'diff_amt' : line['diff_amt'],
                                'lcost' : line['lcost'],
                                'line_subtot' : line['line_subtot'],
                                'dept' : line['dept'],
                                'categ' : line['categ'],
                                'manuftr' : line['manuftr'],
                                'tax' : line['tax'],
                                'igst' : line['igst'],
                                'cgst' : line['cgst'],
                                'sgst' : line['sgst'],
                                'line_taxtot' : line['line_taxtot'],
                                'cess_tot' : line['cess_tot'],
                                'created' : line['created'],
                                'reversal_no' : line['reversal_no'],
                                'reversed_date' : line['reversed_date'],
                                

            })
                       
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'start_date':start_date,
            'end_date':end_date,
            'company_id':company_id,
            'docs':docs,
            }
        

        
        