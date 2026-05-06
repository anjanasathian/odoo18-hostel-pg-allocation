from odoo import fields, models


class HostelDashboard(models.Model):
    _name = 'hostel.dashboard'
    _description = 'Hostel Dashboard'

    name = fields.Char(string='Name', required=True, default='Dashboard')
    total_hostels = fields.Integer(string='Total Hostels', compute='_compute_metrics')
    occupied_rooms = fields.Integer(string='Occupied Rooms', compute='_compute_metrics')
    available_beds = fields.Integer(string='Available Beds', compute='_compute_metrics')
    total_tenants = fields.Integer(string='Total Tenants', compute='_compute_metrics')

    def _compute_metrics(self):
        total_hostels = self.env['hostel.hostel'].sudo().search_count([])

        occupied_room_groups = self.env['hostel.bed'].sudo().read_group(
            [('status', '=', 'occupied'), ('room_id', '!=', False)],
            ['room_id'],
            ['room_id'],
        )
        occupied_rooms = len(occupied_room_groups)

        available_beds = self.env['hostel.bed'].sudo().search_count([('status', '=', 'available')])
        total_tenants = self.env['hostel.tenant'].sudo().search_count([])

        for rec in self:
            rec.total_hostels = total_hostels
            rec.occupied_rooms = occupied_rooms
            rec.available_beds = available_beds
            rec.total_tenants = total_tenants
