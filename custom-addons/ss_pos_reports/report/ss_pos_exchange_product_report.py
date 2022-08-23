# -*- coding: utf-8 -*-

from odoo import models, fields, api
#from pygments.lexer import _inherit


class PosProductReportWizard(models.Model):
    _inherit = 'ss.pos.product.screen.wzd'
   
    def print_pos_wise_exchange_pdf_report(self):
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'start_date':self.start_date if self.start_date else False,
                'end_date':self.end_date if self.end_date else False,
                'cashier_id':self.cashier_id if self.cashier_id else False,
#                 'is_unusedbill':self.is_unusedbill if self.is_unusedbill else False,
                'company_id':self.company_id if self.company_id else False,
                'organization_id':self.organization_id if self.organization_id else False,
            },
        }

        return self.env.ref('ss_pos_reports.ss_pos_wise_exchange_product_report').report_action(self, data=data, config=False)