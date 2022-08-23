from odoo import models, fields, api 


class CashieriseSalesReportWizard(models.Model):
    _inherit = 'cashier.sales.report.screen.wzd.ss'
   
    def print_ss_cashier_sales_pdf_report(self):
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                 'start_date':self.start_date if self.start_date else False,
                 'end_date':self.end_date if self.end_date else False,
                 'company_id':self.company_id if self.company_id else False, 
            },
        }

        return self.env.ref('ss_pos_reports.sales_cashier_details_report_ss').report_action(self, data=data, config=False)