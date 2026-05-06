from odoo import models, fields, api, _

class HostelHostel(models.Model):
    _name= 'hostel.hostel'
    _description = 'Hostel' 

    name = fields.Char(string = 'Hostel Name', required = True)
    phone = fields.Char(string='Phone')
    total_floors = fields.Integer(string='Total Floors')
    category_id = fields.Many2one('hostel.category', string='Category', ondelete='set null')
    facility_ids = fields.Many2many('hostel.facility', string='Facilities')
    room_ids = fields.One2many('hostel.room','hostel_id',string='Rooms')
    room_count = fields.Integer(string='Room Count', compute='_compute_room_count')
    full_room_count = fields.Integer(string='Full Room Count', compute='_compute_room_count')
    available_room_count = fields.Integer(string='Available Room Count', compute='_compute_room_count')

    @api.depends('room_ids', 'room_ids.status')
    def _compute_room_count(self):
        for rec in self:
            rec.room_count = len(rec.room_ids)
            rec.full_room_count = len(rec.room_ids.filtered(lambda r: r.status == 'full'))
            rec.available_room_count = len(rec.room_ids.filtered(lambda r: r.status == 'available'))
        