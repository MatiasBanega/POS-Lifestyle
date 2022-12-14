# -*- coding: utf-8 -*-

from odoo import models, fields, api


class departmentReportWizard(models.Model):
    _inherit = 'sales.summary.screen.wzd'
   
    def print_sales_open_order_pdf_report(self):
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'start_date':self.start_date if self.start_date else False,
                'end_date':self.end_date if self.end_date else False,
                'company_id':self.company_id if self.company_id else False,
            },
        }

        return self.env.ref('ls_pos_reports.sales_Summary_details_report').report_action(self, data=data, config=False)