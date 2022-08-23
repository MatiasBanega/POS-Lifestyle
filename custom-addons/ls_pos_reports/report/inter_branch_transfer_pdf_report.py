from odoo import models
 
class SalesOpenOrdersDetailsReport(models.AbstractModel):    
    _name = 'report.ls_pos_reports.report'
 
    #@api.model
    def _get_report_values(self, docids, data=None):
        start_date = data['form']['start_date'] 
        end_date = data['form']['end_date'] 
        company = data['form']['company']
        
        sql = ''' select 
        branch,inter_branch,description,doc_no,movement_date,code,product_name,brand,product_design,
        item_type,product_color,product_size,transfer_qty,mrp,basic_cost,basic_cost_total,tax,l_cost,
        l_cost_total,department,category,sub_category,vendor,doc_type
        from inter_branch_transfer_screen_line         
        where inter_branch_id=(select max(inter_branch_id) from inter_branch_transfer_screen_line) 
            '''
                
                
        self.env.cr.execute(sql) 
        emp_data = self.env.cr.dictfetchall()
        docs = []
        
        for line in emp_data: 
            
            docs.append({ 
                            'branch' : line['branch'],
                            'inter_branch' : line['inter_branch'],
                            'description' : line['description'],
                            'doc_no' : line['doc_no'],
                            'movement_date' : line['movement_date'],
                            'code' : line['code'],
                            'product_name' : line['product_name'],
                            'brand' : line['brand'],
                            'product_design' : line['product_design'],
                            'item_type' : line['item_type'],
                            'product_color' : line['product_color'],
                            'product_size' : line['product_size'],
                            'transfer_qty' : line['transfer_qty'],
                            'mrp' : line['mrp'],
                            'basic_cost' : line['basic_cost'],
                            'basic_cost_total' : line['basic_cost_total'],
                            'tax' : line['tax'],
                            'l_cost' : line['l_cost'],
                            'l_cost_total' : line['l_cost_total'],
                            'department' : line['department'],
                            'category' : line['category'],
                            'sub_category' : line['sub_category'],
                            'vendor' : line['vendor'],
                            'doc_type' : line['doc_type'],                                
            })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'], 
            'start_date': start_date,
            'end_date': end_date,
            'company': company,
            'docs':docs,
            }
        
        

        
        