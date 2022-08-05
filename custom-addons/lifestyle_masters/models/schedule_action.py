from odoo import api, fields, models

class ScheduledActions(models.Model):
    _name = "schedule.actions"
    
    def master_call(self):
        cash = self.env['cashier.view']
        org = self.env['organization.view']
        ven = self.env['vendor.view']
        com = self.env['company.view']
        cashier=cash.get_cashier()
        organization=org.get_organization()
        vendor=ven.get_vendor()
        company=com.get_company()
        
        
        
