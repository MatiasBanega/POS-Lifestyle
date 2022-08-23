from odoo import models, fields, api

class StockReportWizard(models.Model):
    _inherit = 'stock.adjustment.screen.wizard'
   
    def print_stock_adjust_pdf_report(self):
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'start_date':self.start_date if self.start_date else False,
                'end_date':self.end_date if self.end_date else False,
                'company_id':self.company_id if self.company_id else False,
                'department':self.department if self.department else False,
                'product_category':self.product_category if self.product_category else False,
                'product_sub_category':self.product_sub_category if self.product_sub_category else False,
                'product_brand':self.product_brand if self.product_brand else False,
                'vendors':self.vendors if self.vendors else False,
            },
        }

        return self.env.ref('ls_pos_reports.stock_adjustment_detailed_report').report_action(self, data=data, config=False)