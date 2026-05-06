from odoo import models, fields, api, _


class HostelCategory(models.Model):
    _name = 'hostel.category'
    _description = 'Hostel Category'

    name = fields.Char(string='Category Name', required=True)
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    color = fields.Integer(string='Color Index', default=0)

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Category name must be unique!'),
    ]
