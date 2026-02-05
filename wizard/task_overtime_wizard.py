from odoo import models, fields
from odoo.exceptions import UserError

class SaleExcelExportWizard(models.TransientModel):
    _name = 'task.overtime.wizard'

    date = fields.Date(required=True)
    from_time = fields.Float(string="From", required=True)
    to_time = fields.Float(string="To", required=True)
    type = fields.Selection([
        ('work_hours', 'Work Hours'),
        ('weekend', 'Weekend'),
    ], required=True)

    def create_overtime_action(self):
        self.ensure_one()
        task_id = self.env.context.get('task_id')
        employee = self.env.user.employee_id
        if not employee:
            raise UserError("Your user is not linked to an employee.")

        overtime = self.env['hr.overtime'].create({
            'employee_id': employee.id,
            'date': self.date,
            'type': self.type,
            'line_ids': [(0, 0, {
                'task_id': task_id,
                'date': self.date,
                'from_time': self.from_time,
                'to_time': self.to_time,
            })],
        })
        return {'type': 'ir.actions.act_window_close'}