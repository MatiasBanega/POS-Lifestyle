# -*- coding: utf-8 -*-

from odoo import models, fields, api
#from pygments.lexer import _inherit


class departmentReportWizard(models.Model):
    _inherit = 'inter.branch.transfer.screen.wzd'
   
    def print_inter_branch_transfer_pdf_report(self):
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'start_date':self.start_date if self.start_date else False,
                'end_date':self.end_date if self.end_date else False,
                'company':self.company if self.company else False,
            },
        }

        return self.env.ref('ls_pos_reports.item_transfer_details_report').report_action(self, data=data, config=False)