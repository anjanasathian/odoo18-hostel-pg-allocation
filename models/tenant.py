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
    room_id = fields.Many2one('hostel.room', string='Room', domain=[('status', '=', 'available')])
    bed_id = fields.Many2one('hostel.bed', string='Bed', ondelete='set null', domain=[('status', '=', 'available')])
    check_in_date = fields.Date(string='Check-in Date')
    check_out_date = fields.Date(string='Check-out Date')
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], default='active')    
    invoice_id = fields.Many2one('hostel.invoice', string='Invoice')
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('tenant_id') or vals.get('tenant_id') == '-':
                vals['tenant_id'] = self.env['ir.sequence'].next_by_code('hostel.tenant.id') or '-'
        tenants = super().create(vals_list)
        
        # Update tenant_id in bed record
        for tenant in tenants:
            if tenant.bed_id:
                tenant.bed_id.tenant_id = tenant.id
                tenant.bed_id.status = 'occupied'
        
        return tenants

    def write(self, vals):
        result = super().write(vals)
        
        # Update tenant_id in bed record if bed_id is changed
        if 'bed_id' in vals:
            for record in self:
                if record.bed_id:
                    record.bed_id.tenant_id = record.id
                    record.bed_id.status = 'occupied'
                else:
                    # If bed_id is set to null, also update the bed
                    old_bed = self.env['hostel.bed'].search([('tenant_id', '=', record.id)], limit=1)
                    if old_bed:
                        old_bed.tenant_id = False
                        old_bed.status = 'available'
                    pass
        
        return result
    
    def unlink(self):
        # Before deleting tenant, set bed to available
        for record in self:
            if record.bed_id:
                record.bed_id.tenant_id = False
                record.bed_id.status = 'available'
        return super().unlink()

    def action_check_out(self):
        today = fields.Date.context_today(self)
        for record in self:
            record.write({
                'status': 'inactive',
                'check_out_date': today,
            })

            if not record.invoice_id:
                invoice = self.env['hostel.invoice'].create({
                    'tenant_id': record.id,
                    'billing_from': record.check_in_date or today,
                    'billing_to': record.check_out_date or today,
                    'daily_rate': 0.0,
                })
                record.invoice_id = invoice.id

            if record.bed_id:
                record.bed_id.write({
                    'tenant_id': False,
                    'status': 'available',
                })
            record.write({
                'bed_id': False,
            })
        return True

    def action_view_invoice(self):
        self.ensure_one()
        if self.invoice_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Invoice',
                'res_model': 'hostel.invoice',
                'view_mode': 'form',
                'views': [(False, 'form')],
                'res_id': self.invoice_id.id,
            }

        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'hostel.invoice',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'context': {
                'default_tenant_id': self.id,
                'default_billing_from': self.check_in_date,
                'default_billing_to': self.check_out_date or fields.Date.context_today(self),
                'default_daily_rate': 0.0,
            },
        }
    
    @api.constrains('check_in_date', 'check_out_date')
    def _check_checkout_after_checkin(self):
        for record in self:
            if record.check_in_date and record.check_out_date:
                if record.check_out_date <= record.check_in_date:
                    raise ValidationError('Check-out date must be after the check-in date.')

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
            
    