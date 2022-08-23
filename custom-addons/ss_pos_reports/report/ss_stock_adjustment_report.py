from odoo import models, fields, api

class SS_StockReportWizard(models.Model):
    _inherit = 'super.stock.adjustment.screen.wizard'
   
    def print_ss_stock_adjust_pdf_report(self):
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'start_date':self.start_date if self.start_date else False,
                'end_date':self.end_date if self.end_date else False,
                'company_id':self.company_id if self.company_id else False,
                'organization_id':self.organization_id if self.organization_id else False,
                'ss_department':self.ss_department if self.ss_department else False,
                'ss_product_category':self.ss_product_category if self.ss_product_category else False,
                'ss_product_sub_category':self.ss_product_sub_category if self.ss_product_sub_category else False,
                'ss_product_brand':self.ss_product_brand if self.ss_product_brand else False,
                'ss_vendors':self.ss_vendors if self.ss_vendors else False,
            },
        }

        return self.env.ref('ss_pos_reports.ss_stock_adjustment_detailed_report').report_action(self, data=data, config=False)