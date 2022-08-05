# -*- coding: utf-8 -*-

from odoo import models, fields, api
#from pygments.lexer import _inherit


class PosProductReportWizard(models.Model):
    _inherit = 'pos.product.screen.wzd'
   
    def print_pos_wise_exchange_pdf_report(self):
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'start_date':self.start_date if self.start_date else False,
                'end_date':self.end_date if self.end_date else False,
                'cashier_id':self.cashier_id.name if self.cashier_id.name else False,
                'is_unusedbill':self.is_unusedbill if self.is_unusedbill else False,
                'company_id':self.company_id if self.company_id else False,
            },
        }

        return self.env.ref('ls_pos_reports.pos_wise_exchange_product_report').report_action(self, data=data, config=False)