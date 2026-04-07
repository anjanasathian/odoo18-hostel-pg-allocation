from odoo import models, fields, api    

class HostelBed(models.Model):
    _name = 'hostel.bed'
    _description = 'Hostel Bed'

    name = fields.Char(string='Bed Number', required=True, copy=False, readonly=True, default='-')
    room_id = fields.Many2one('hostel.room', string='Room', required=True, ondelete='cascade')
    status = fields.Selection([
        ('available','Available'),
        ('occupied','Occupied')
    ], default='available')
    tenant_id = fields.Many2one('hostel.tenant', string='Tenant')   


                       
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if not vals.get('name') or vals.get('name') == '-':
            vals['name'] = self.env['ir.sequence'].next_by_code('hostel.bed') or '-'
    return super().create(vals_list)