from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HoselTenant(models.Model):
    _name = 'hostel.tenant'
    _description = 'Hostel Tenant'

    name = fields.Char(string='Tenant Name', required=True)
    tenant_id = fields.Char(string='Tenant ID', required=True, copy=False, readonly=True, default='-')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    address = fields.Text(string='Address')
    hostel_id = fields.Many2one('hostel.hostel', string='Hostel', ondelete='set null')
    bed_id = fields.Many2one('hostel.bed', string='Bed', ondelete='set null')
    room_id = fields.Many2one('hostel.room', string='Room', related='bed_id.room_id', store=True, readonly=True)
    check_in_date = fields.Date(string='Check-in Date')
    check_out_date = fields.Date(string='Check-out Date')
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], default='active')    

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == '-':
                vals['name'] = self.env['ir.sequence'].next_by_code('hostel.tenant') or '-'
        return super().create(vals_list)

    @api.constrains('bed_id')
    def _check_bed_availability(self):
        for record in self:
            if not record.bed_id:
                continue

            existing_tenant = self.search([
                ('bed_id', '=', record.bed_id.id),
                ('id', '!=', record.id),
                ('status', '=', 'active'),
            ], limit=1)
            if existing_tenant:
                raise ValidationError('The selected bed is already assigned to another active tenant.')