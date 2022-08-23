from datetime import datetime, timedelta
 
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

 
class SS_StockBillReport(models.AbstractModel):    
    _name = 'report.ss_pos_reports.ss_report_stock_adjustment'
 
    
    def _get_report_values(self, docids, data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        company_id = data['form']['company_id']
        organization_id = data['form']['organization_id'] 
        ss_department = data['form']['ss_department']
        ss_product_category = data['form']['ss_product_category']
        ss_product_sub_category = data['form']['ss_product_sub_category']
        ss_product_brand = data['form']['ss_product_brand']
        ss_vendors = data['form']['ss_vendors']


        
        sql = '''       
              select ss_branch,ss_description,ss_doc_number,ss_date,ss_code,ss_pdt_name,
                    ss_adjustment_qty,ss_mrp_rate,ss_l_cost,ss_l_cost_total,ss_fgc,ss_fgc_total,ss_tax_total,ss_depart_ment,ss_category,
                    ss_sub_category,ss_brand,ss_vendor,ss_doc_type,ss_sub_doc_type,ss_inv_sub_type from
                    super_stock_adjustment_line         
                    where stock_order=(select max(stock_order) from  super_stock_adjustment_line )
                      
                '''
                
        self.env.cr.execute(sql) 
        bill_data = self.env.cr.dictfetchall()
        docs = []
        seq = 0
        for line in bill_data: 
                                   
            docs.append({ 
                                'ss_branch' : line['ss_branch'],
                                'ss_description' : line['ss_description'],
                                'ss_doc_number' : line['ss_doc_number'],
                                'ss_date' : line['ss_date'],
                                'ss_code' : line['ss_code'],
                                'ss_pdt_name' : line['ss_pdt_name'],
                                'ss_adjustment_qty' : line['ss_adjustment_qty'],
                                'ss_mrp_rate' : line['ss_mrp_rate'],
                                'ss_l_cost' : line['ss_l_cost'],
                                'ss_l_cost_total' : line['ss_l_cost_total'],
                                'ss_fgc' :line['ss_fgc'],
                                'ss_fgc_total' :line['ss_fgc_total'],
                                'ss_tax_total' :line['ss_tax_total'],
                                'ss_depart_ment' : line['ss_depart_ment'],
                                'ss_category' : line['ss_category'],
                                'ss_sub_category' : line['ss_sub_category'],
                                'ss_brand' : line['ss_brand'],
                                'ss_vendor' :line['ss_vendor'],
                                'ss_doc_type' : line['ss_doc_type'],
                                'ss_sub_doc_type' : line['ss_sub_doc_type'],
                                'ss_inv_sub_type' : line['ss_inv_sub_type'],
            })
                       
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'], 
            'start_date':start_date,
            'end_date':end_date,
            'company_id':company_id,
            'organization_id':organization_id,
            'ss_department':ss_department,
            'ss_product_category':ss_product_category,
            'ss_product_sub_category':ss_product_sub_category,
            'ss_product_brand':ss_product_brand,
            'ss_vendors':ss_vendors,
            'docs':docs,
            }
        