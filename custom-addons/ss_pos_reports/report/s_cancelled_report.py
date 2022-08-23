from odoo import models, fields, api

class SuperCancelReportWizard(models.Model):
    _inherit = 'ss.item.wise.cancel.screen.wzd'
   
    def print_ss_cancel_bill_pdf_report(self):
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'start_date':self.start_date if self.start_date else False,
                'end_date':self.end_date if self.end_date else False,
                'company_id':self.company_id if self.company_id else False,
            },
        }

        return self.env.ref('ss_pos_reports.super_itemwise_detailed_cancel_report').report_action(self, data=data, config=False)