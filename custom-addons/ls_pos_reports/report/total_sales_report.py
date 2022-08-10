from odoo import models

class totalsalesReportWizard(models.Model):
    _inherit = 'total.screen.wzd'
   
    def print_total_pdf_report(self):
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'start_date':self.start_date if self.start_date else False,
                'end_date':self.end_date if self.end_date else False,
                'company_id':self.company_id if self.company_id else False,
                'online_sales':self.online_sales if self.online_sales else False,
            },
        }

        return self.env.ref('ls_pos_reports.total_sales_report_pdf').report_action(self, data=data, config=False)
