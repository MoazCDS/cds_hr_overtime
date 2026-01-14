from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    overtime_approver_id = fields.Many2one('res.users', string="Overtime")
    overtime_rate = fields.Integer()