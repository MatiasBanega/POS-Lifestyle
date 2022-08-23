from datetime import datetime, timedelta
 
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

 
class StockBillReport(models.AbstractModel):    
    _name = 'report.ls_pos_reports.report_stock_adjustment'
 
    
    def _get_report_values(self, docids, data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        company_id = data['form']['company_id']
        department = data['form']['department']
        product_category = data['form']['product_category']
        product_sub_category = data['form']['product_sub_category']
        product_brand = data['form']['product_brand']
        vendors = data['form']['vendors']

        
        sql = '''       
               select branch,description,doc_number,s_date,code,pdt_name,brand,itemtype,
               pdt_design,pdt_color,pdt_size,
                   
                    adjustment_qty,mrp_rate,l_cost,l_cost_total,fgc,fgc_total,
                    tax_total,depart_ment,category,
                    sub_category,vendor,doc_type,sub_doc_type,inv_sub_type from
                    stock_adjustment_line         
                    where stock_id=(select max(stock_id) from  stock_adjustment_line )
                '''
                
        self.env.cr.execute(sql) 
        cbill_data = self.env.cr.dictfetchall()
        docs = []
        seq = 0
        for line in cbill_data: 
                                   
            docs.append({ 
                                'branch' : line['branch'],
                                'description' : line['description'],
                                'doc_number' : line['doc_number'],
                                's_date' : line['s_date'],
                                'code' : line['code'],
                                'pdt_name' : line['pdt_name'],
                                'brand' : line['brand'],
                                'itemtype' :line['itemtype'],
                                'pdt_design' :line['pdt_design'],
                                'pdt_color' :line['pdt_color'],
                                'pdt_size' :line['pdt_size'],
                                'adjustment_qty' : line['adjustment_qty'],
                                'mrp_rate' : line['mrp_rate'],
                                'l_cost' : line['l_cost'],
                                'l_cost_total' : line['l_cost_total'],
                                'fgc' :line['fgc'],
                                'fgc_total' :line['fgc_total'],
                                'tax_total' :line['tax_total'],
                                'depart_ment' : line['depart_ment'],
                                'category' : line['category'],
                                'sub_category' : line['sub_category'],
                                'vendor' :line['vendor'],
                                'doc_type' : line['doc_type'],
                                'sub_doc_type' : line['sub_doc_type'],
                                'inv_sub_type' : line['inv_sub_type'],
            })
                       
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'], 
            'start_date':start_date,
            'end_date':end_date,
            'company_id':company_id,
            'department':department,
            'product_category':product_category,
            'product_sub_category':product_sub_category,
            'product_brand':product_brand,
            'vendors':vendors,
            'docs':docs,
            }
        