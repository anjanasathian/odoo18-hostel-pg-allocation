from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class HoselTenant(models.Model):
    _name = 'hostel.tenant'
    _description = 'Hostel Tenant'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Tenant Name', required=True)
    tenant_id = fields.Char(string='Tenant ID', required=True, copy=False, readonly=True, default='-')
    email = fields.Char(string='Email', tracking=True)
    phone = fields.Char(string='Phone')
    address = fields.Text(string='Address')
    hostel_id = fields.Many2one('hostel.hostel', string='Hostel', ondelete='set null', tracking=True)
    room_id = fields.Many2one(
        'hostel.room',
        string='Room',
        domain="[('hostel_id', '=', hostel_id), ('status', '=', 'available')]",
        tracking=True,
    )
    bed_id = fields.Many2one(
        'hostel.bed',
        string='Bed',
        ondelete='set null',
        domain="[('room_id', '=', room_id), ('status', '=', 'available')]",
        tracking=True,
    )
    check_in_date = fields.Date(string='Check-in Date')
    check_out_date = fields.Date(string='Check-out Date')
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], default='active', tracking=True)
    invoice_id = fields.Many2one('hostel.invoice', string='Invoice')

    def _send_bed_assignment_email(self):
        template = self.env.ref('hostel_allocation.mail_template_tenant_bed_assignment', raise_if_not_found=False)
        if not template:
            _logger.warning('Bed assignment email template not found: hostel_allocation.mail_template_tenant_bed_assignment')
            return

        for record in self.filtered(lambda r: r.email and r.bed_id):
            try:
                template.sudo().send_mail(
                    record.id,
                    force_send=True,
                    raise_exception=True,
                    email_values={'email_to': record.email},
                )
                record.message_post(body=_('Bed assignment email sent to %s') % record.email)
            except Exception as err:
                _logger.exception('Failed to send bed assignment email for tenant %s', record.id)
                record.message_post(
                    body=_('Failed to send bed assignment email to %s. Error: %s') % (record.email, str(err))
                )

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
                tenant._send_bed_assignment_email()
        
        return tenants

    def write(self, vals):
        old_bed_by_tenant = {}
        if 'bed_id' in vals:
            old_bed_by_tenant = {record.id: record.bed_id for record in self}

        result = super().write(vals)
        
        # Update tenant_id in bed record if bed_id is changed
        if 'bed_id' in vals:
            for record in self:
                old_bed = old_bed_by_tenant.get(record.id)

                if old_bed and old_bed != record.bed_id:
                    old_bed.tenant_id = False
                    old_bed.status = 'available'

                if record.bed_id:
                    record.bed_id.tenant_id = record.id
                    record.bed_id.status = 'occupied'
                    if record.bed_id != old_bed:
                        record._send_bed_assignment_email()
                else:
                    if old_bed:
                        old_bed.tenant_id = False
                        old_bed.status = 'available'
        
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
            checkout_date = today
            if record.check_in_date and checkout_date <= record.check_in_date:
                if record.check_out_date and record.check_out_date > record.check_in_date:
                    checkout_date = record.check_out_date
                else:
                    raise ValidationError(_('Cannot check out on or before the check-in date.'))

            record.write({
                'status': 'inactive',
                'check_out_date': checkout_date,
            })

            if not record.invoice_id:
                invoice = self.env['hostel.invoice'].create({
                    'tenant_id': record.id,
                    'billing_from': record.check_in_date or today,
                    'billing_to': record.check_out_date or checkout_date,
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

    @api.onchange('hostel_id')
    def _onchange_hostel_id(self):
        for record in self:
            if record.room_id and record.room_id.hostel_id != record.hostel_id:
                record.room_id = False
            if record.bed_id and (not record.room_id or record.bed_id.room_id != record.room_id):
                record.bed_id = False

    @api.onchange('room_id')
    def _onchange_room_id(self):
        for record in self:
            if record.bed_id and record.bed_id.room_id != record.room_id:
                record.bed_id = False
    
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

    @api.constrains('hostel_id', 'room_id')
    def _check_room_matches_hostel(self):
        for record in self:
            if record.hostel_id and record.room_id and record.room_id.hostel_id != record.hostel_id:
                raise ValidationError(_('The selected room does not belong to the selected hostel.'))

    @api.constrains('room_id', 'bed_id')
    def _check_bed_matches_room(self):
        for record in self:
            if record.room_id and record.bed_id and record.bed_id.room_id != record.room_id:
                raise ValidationError(_('The selected bed does not belong to the selected room.'))
            
    