from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    def create_overtime(self):
        action = self.env['ir.actions.actions']._for_xml_id('cds_hr_overtime.create_overtime_wizard_action')
        action['context'] = {'task_id': self.id}
        return action