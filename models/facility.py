from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HostelFacility(models.Model):
    _name = 'hostel.facility'
    _description = 'Hostel Facility'
    _order = 'sequence, name'

    name = fields.Char(string='Facility Name', required=True)
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Sequence', default=10,
                              help='Used to order facilities. Lower sequence appears first.')
    color = fields.Integer(string='Color Index', default=0)
    facility_type = fields.Selection([
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('recreational', 'Recreational'),
        ('utilities', 'Utilities'),
        ('security', 'Security'),
    ], string='Facility Type', default='basic', required=True)
    hostel_count = fields.Integer(
        string='Hostels',
        compute='_compute_hostel_count',
        help='Number of hostels that offer this facility.',
    )

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Facility name must be unique!'),
        ('code_unique', 'UNIQUE(code)', 'Facility code must be unique!'),
    ]

    # -------------------------------------------------------------------------
    # Compute Methods
    # -------------------------------------------------------------------------

    def _compute_hostel_count(self):
        for rec in self:
            rec.hostel_count = self.env['hostel.hostel'].search_count(
                [('facility_ids', 'in', rec.id)]
            )

    # -------------------------------------------------------------------------
    # Onchange Methods
    # -------------------------------------------------------------------------

    @api.onchange('name')
    def _onchange_name_generate_code(self):
        """Auto-generate a code from the facility name if code is not set."""
        if self.name and not self.code:
            self.code = self.name[:6].upper().replace(' ', '_')

    # -------------------------------------------------------------------------
    # Constraints
    # -------------------------------------------------------------------------

    @api.constrains('code')
    def _check_code_format(self):
        for rec in self:
            if rec.code and not rec.code.replace('_', '').isalnum():
                raise ValidationError(
                    _('Code "%s" should only contain alphanumeric characters or underscores.') % rec.code
                )

    # -------------------------------------------------------------------------
    # Action Methods
    # -------------------------------------------------------------------------

    def action_view_hostels(self):
        """Open the list of hostels that offer this facility."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Hostels with "%s"') % self.name,
            'res_model': 'hostel.hostel',
            'view_mode': 'list,form',
            'domain': [('facility_ids', 'in', self.id)],
            'context': {'default_facility_ids': [(4, self.id)]},
        }
