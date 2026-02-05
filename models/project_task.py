from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    overtime_line_ids = fields.One2many(
        'hr.overtime.lines',
        'task_id',
        string="Overtime Lines"
    )

    overtime_count = fields.Integer(compute="_compute_overtime_count")

    def _compute_overtime_count(self):
        for rec in self:
            rec.overtime_count = len(rec.overtime_line_ids)

    def create_overtime(self):
        action = self.env['ir.actions.actions']._for_xml_id('cds_hr_overtime.create_overtime_wizard_action')
        action['context'] = {'task_id': self.id}
        return action