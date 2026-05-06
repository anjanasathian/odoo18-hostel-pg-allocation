from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HostelMess(models.Model):
    _name = 'hostel.mess'
    _description = 'Hostel Mess / Food Management'
    _order = 'hostel_id, name'

    name = fields.Char(string='Plan Name', required=True)
    hostel_id = fields.Many2one(
        'hostel.hostel', string='Hostel',
        ondelete='cascade',
        help='Hostel this mess plan belongs to.',
    )
    meal_type = fields.Selection([
        ('veg', 'Vegetarian'),
        ('non_veg', 'Non-Vegetarian'),
        ('both', 'Both'),
    ], string='Meal Type', required=True, default='both')
    plan_type = fields.Selection([
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
    ], string='Plan Type', required=True, default='monthly')
    price = fields.Float(string='Price', digits=(16, 2))
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    tenant_count = fields.Integer(
        string='Tenants Enrolled',
        compute='_compute_tenant_count',
    )

    _sql_constraints = [
        ('name_hostel_unique', 'UNIQUE(name, hostel_id)',
         'A mess plan with this name already exists for the selected hostel!'),
    ]

    # -------------------------------------------------------------------------
    # Compute Methods
    # -------------------------------------------------------------------------

    def _compute_tenant_count(self):
        for rec in self:
            rec.tenant_count = self.env['hostel.tenant'].search_count(
                [('mess_id', '=', rec.id)]
            )

    # -------------------------------------------------------------------------
    # Constraints
    # -------------------------------------------------------------------------

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.end_date < rec.start_date:
                raise ValidationError(_('End date cannot be before start date.'))

    @api.constrains('price')
    def _check_price(self):
        for rec in self:
            if rec.price < 0:
                raise ValidationError(_('Price cannot be negative.'))

    # -------------------------------------------------------------------------
    # Onchange Methods
    # -------------------------------------------------------------------------

    @api.onchange('plan_type')
    def _onchange_plan_type(self):
        """Suggest a name when plan type changes."""
        if self.plan_type and not self.name:
            self.name = dict(self._fields['plan_type'].selection).get(self.plan_type, '')

    # -------------------------------------------------------------------------
    # Action Methods
    # -------------------------------------------------------------------------

    def action_view_tenants(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tenants on "%s"') % self.name,
            'res_model': 'hostel.tenant',
            'view_mode': 'list,form',
            'domain': [('mess_id', '=', self.id)],
            'context': {'default_mess_id': self.id},
        }
