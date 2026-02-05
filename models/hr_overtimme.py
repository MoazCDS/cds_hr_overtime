from odoo import models, fields, api

class HrOvertime(models.Model):
    _name = 'hr.overtime'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', readonly=True)
    date = fields.Date(required=True)
    line_ids = fields.One2many('hr.overtime.lines', 'overtime_id')
    total_time = fields.Float(string="Total Time(hrs)", compute="_compute_total_time", store=True, readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
    ], default='draft')
    type = fields.Selection([
        ('weekend', 'Weekend'),
        ('work_hours', 'Work Hours'),
    ], required=True)
    is_overtime_approver = fields.Boolean(compute="_compute_is_overtime_approver_manager")
    is_overtime_manager = fields.Boolean(compute="_compute_is_overtime_approver_manager")
    payment_id = fields.Many2one('account.payment', readonly=True)
    payment_count = fields.Integer(compute='_compute_payment_count')

    @api.depends('payment_id')
    def _compute_payment_count(self):
        for rec in self:
            rec.payment_count = 1 if rec.payment_id else 0

    @api.depends('employee_id')
    def _compute_is_overtime_approver_manager(self):
        for rec in self:
            rec.is_overtime_approver = False
            if rec.employee_id:
                if rec.is_overtime_approver:
                    if rec.employee_id.is_overtime_approver_id == self.env.user:
                        rec.is_overtime_approver = True
            if self.env.user.has_group('cds_hr_overtime.hr_overtime_manager_group'):
                rec.is_overtime_manager = True
            else: rec.is_overtime_manager = False

    def create(self, vals_list):
        if self.env.user.has_group('cds_hr_overtime.hr_overtime_manager_group'):
            return super().create(vals_list)
        if not vals_list.get('employee_id') :
            vals_list['employee_id'] = self.env.user.employee_id.id
        return super().create(vals_list)


    @api.depends('line_ids')
    def _compute_total_time(self):
        for rec in self:
            total_time = 0
            for line in rec.line_ids:
                total_time += (line.to_time - line.from_time)
            rec.total_time = total_time

    def change_state(self):
        state = self.env.context.get('state')
        for rec in self:
            rec.state = state
            if state == 'paid':
                payment = self.env['account.payment'].create({
                    'state': 'draft',
                    'payment_type': 'inbound',
                    'partner_id': rec.employee_id.address_id.id,
                    'amount': rec.total_time * rec.employee_id.overtime_rate if rec.employee_id.overtime_rate else 0,
                    'date': rec.date,
                })
                rec.payment_id = payment.id
                return payment

    def action_view_payment(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment',
            'view_mode': 'form',
            'res_model': 'account.payment',
            'res_id': self.payment_id.id,
            'target': 'current',
        }

class HrOvertimeLines(models.Model):
    _name = 'hr.overtime.lines'

    task_id = fields.Many2one('project.task', required=True)
    overtime_id = fields.Many2one('hr.overtime')
    date = fields.Date(required=True)
    from_time = fields.Float(string="From" ,required=True)
    to_time = fields.Float(string="To", required=True)
    total_time = fields.Float(string="Total Time(hrs)", compute="_compute_total_time", store=True, readonly=True)

    @api.depends('from_time', 'to_time')
    def _compute_total_time(self):
        for rec in self:
            if rec.from_time and rec.to_time:
                total_time = (rec.to_time - rec.from_time)
                rec.total_time = total_time
            else: rec.total_time = 0