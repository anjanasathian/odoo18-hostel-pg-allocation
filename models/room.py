from odoo import models, fields, api, _

class HostelRoom(models.Model):
    _name = 'hostel.room'
    _description = 'Hostel Room'

    name = fields.Char(string='Room Number', required=True, copy=False, readonly=True, default='-')
    hostel_id = fields.Many2one('hostel.hostel', string='Hostel', required=True, ondelete='cascade')
    floor = fields.Integer(string='Floor')

    capacity = fields.Integer(string='Capacity')

    status = fields.Selection([
        ('available','Available'),
        ('full','Full')
    ], default='available')

@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if not vals.get('name') or vals.get('name') == '-':
            vals['name'] = self.env['ir.sequence'].next_by_code('service.booking') or '-'
    return super().create(vals_list)
