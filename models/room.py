from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HostelRoom(models.Model):
    _name = 'hostel.room'
    _description = 'Hostel Room'

    name = fields.Char(string='Room Number', required=True, copy=False, readonly=True, default='-')
    hostel_id = fields.Many2one('hostel.hostel', string='Hostel', required=True, ondelete='cascade')
    floor = fields.Integer(string='Floor')

    capacity = fields.Integer(string='Capacity')
    bed_ids = fields.One2many('hostel.bed', 'room_id', string='Beds')
    bed_count = fields.Integer(string='Bed Count', compute='_compute_bed_count')
    available_bed_count = fields.Integer(string='Available Bed Count', compute='_compute_bed_count')
    full_bed_count = fields.Integer(string='Full Bed Count', compute='_compute_bed_count')
    occupied_bed_count = fields.Integer(string='Occupied Bed Count', compute='_compute_bed_count')

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

@api.depends('bed_ids', 'bed_ids.status')
def _compute_bed_count(self):
    for rec in self:
        rec.bed_count = len(rec.bed_ids)
        rec.occupied_bed_count = len(rec.bed_ids.filtered(lambda b: b.status == 'occupied'))
        rec.available_bed_count = len(rec.bed_ids.filtered(lambda b: b.status == 'available'))

@api.depends('bed_ids', 'bed_ids.status', 'capacity')
def _compute_status(self):
    for rec in self:
        if rec.capacity > 0 and rec.occupied_bed_count >= rec.capacity:
            rec.status = 'full'
        else:
            rec.status = 'available'
@api.constrains('capacity')
def _check_capacity_positive(self):
    for rec in self:
        if rec.capacity <= 0:
            raise ValidationError('Room capacity must be greater than 0.')