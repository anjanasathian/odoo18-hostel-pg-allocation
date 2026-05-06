from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HostelInvoice(models.Model):
    _name = 'hostel.invoice'
    _description = 'Hostel Invoice'

    invoice_number = fields.Char(string='Invoice Number', copy=False, readonly=True, default='-')
    tenant_id = fields.Many2one('hostel.tenant', string='Tenant', required=True)
    invoice_date = fields.Date(string='Invoice Date', default=fields.Date.context_today, required=True)
    name = fields.Char(string='Name', compute='_compute_name', store=True, readonly=False)
    email = fields.Char(string='Email', compute='_compute_from_tenant', store=True, readonly=False)
    phone = fields.Char(string='Phone', compute='_compute_from_tenant', store=True, readonly=False)
    address = fields.Text(string='Address', compute='_compute_from_tenant', store=True, readonly=False)
    hostel_id = fields.Many2one('hostel.hostel', string='Hostel', compute='_compute_from_tenant', store=True, readonly=False)   
    room_id = fields.Many2one('hostel.room', string='Room', compute='_compute_from_tenant', store=True, readonly=False)
    bed_id = fields.Many2one('hostel.bed', string='Bed', compute='_compute_from_tenant', store=True, readonly=False)
    invoice_date = fields.Date(string='Invoice Date', default=fields.Date.context_today, required=True)
    check_in_date = fields.Date(string='Check-in Date', compute='_compute_from_tenant', store=True, readonly=False)
    check_out_date = fields.Date(string='Check-out Date', compute='_compute_from_tenant', store=True, readonly=False)
    total_days = fields.Integer(string='Total Days', compute='_compute_total_days', store=True)
    billing_from = fields.Date(string='Billing From', required=True, store=True)
    billing_to = fields.Date(string='Billing To', required=True, store=True)
    daily_rate = fields.Float(string='Daily Rate', required=True)
    mess_id = fields.Many2one('hostel.mess', string='Mess Plan',
                              compute='_compute_from_tenant', store=True, readonly=False)
    mess_charge = fields.Float(string='Mess Charge', compute='_compute_amount_total', store=True)
    amount_total = fields.Float(string='Total Amount', compute='_compute_amount_total', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], default='draft', string="Status")
    notes = fields.Text(string='Notes')     

    @api.depends('tenant_id')
    def _compute_name(self):
        for record in self:
            record.name = record.tenant_id.name if record.tenant_id else ''

    @api.depends('tenant_id')
    def _compute_from_tenant(self):
        for record in self:
            tenant = record.tenant_id
            record.email = tenant.email if tenant else False
            record.phone = tenant.phone if tenant else False
            record.address = tenant.address if tenant else False
            record.hostel_id = tenant.hostel_id if tenant else False
            record.room_id = tenant.room_id if tenant else False
            record.bed_id = tenant.bed_id if tenant else False
            record.check_in_date = tenant.check_in_date if tenant else False
            record.check_out_date = tenant.check_out_date if tenant else False
            record.mess_id = tenant.mess_id if tenant else False

    @api.depends('billing_from', 'billing_to')
    def _compute_total_days(self):
        for record in self:
            if record.billing_from and record.billing_to:
                record.total_days = (record.billing_to - record.billing_from).days +1
            else:
                record.total_days = 0
    
    @api.depends('total_days', 'daily_rate', 'mess_id', 'mess_id.price', 'mess_id.plan_type')
    def _compute_amount_total(self):
        for record in self:
            accommodation = record.total_days * record.daily_rate
            mess_charge = 0.0
            if record.mess_id and record.mess_id.price:
                if record.mess_id.plan_type == 'daily':
                    mess_charge = record.total_days * record.mess_id.price
                else:  # monthly
                    months = (record.total_days / 30.0) if record.total_days else 0
                    mess_charge = months * record.mess_id.price
            record.mess_charge = mess_charge
            record.amount_total = accommodation + mess_charge

    def action_draft(self):
        self.state = 'draft'

    def action_paid(self):
        self.state = 'paid'

    def action_cancel(self):
        self.state = 'cancelled'

    @api.constrains('check_in_date', 'check_out_date')
    def _check_dates(self):
        for record in self:
            if record.check_in_date and record.check_out_date:
                if record.check_out_date < record.check_in_date:
                    raise ValidationError('Check-out date cannot be before check-in date.') 
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('invoice_number') or vals.get('invoice_number') == '-':
                vals['invoice_number'] = self.env['ir.sequence'].next_by_code('hostel.invoice') or '-'
        return super().create(vals_list)
    
    @api.constrains('billing_from', 'billing_to')
    def _check_billing_dates(self):
        for record in self:
            if record.billing_from and record.billing_to:
                if record.billing_to < record.billing_from:
                    raise ValidationError('Billing end date cannot be before billing start date.')