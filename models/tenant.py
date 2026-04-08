from odoo import models, fields, api

class HoselTenant(models.Model):
    _name = 'hostel.tenant'
    _description = 'Hostel Tenant'

    name = fields.Char(string='Tenant Name', required=True)
    tenant_id = fields.Char(string='Tenant ID', required=True, copy=False, readonly=True, default='-')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    address = fields.Text(string='Address')
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
