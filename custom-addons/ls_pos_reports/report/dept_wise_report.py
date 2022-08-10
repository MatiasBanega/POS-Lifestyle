# -*- coding: utf-8 -*-

from odoo import models, fields, api
#from pygments.lexer import _inherit


class deptwiseReportWizard(models.Model):
    _inherit = 'dept.screen.wzd'
   
    def print_dept_pdf_report(self):
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'start_date':self.start_date if self.start_date else False,
                'end_date':self.end_date if self.end_date else False,
                'company_id':self.company_id if self.company_id else False,
            },
        }

        return self.env.ref('ls_pos_reports.dept_wise_sales_report_pdf').report_action(self, data=data, config=False)
