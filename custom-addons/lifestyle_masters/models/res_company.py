from odoo import api, fields, models


class InheritCompany(models.Model):
    _inherit="res.company"
    
    organization_id=fields.Many2one('organization.master',String="Organization",store=True)