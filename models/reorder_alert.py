from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ReorderAlert(models.Model):
    _name = 'inventory.reorder.alert'
    _description = 'Reorder Alert'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Reference',
        required=True,
        readonly=True,
        default='New',
        copy=False)

    product_id = fields.Many2one(
        'inventory.product',
        string='Product',
        required=True,
        tracking=True)

    warehouse_id = fields.Many2one(
        'inventory.warehouse',
        string='Warehouse',
        required=True,
        tracking=True)

    location_id = fields.Many2one(
        'inventory.stock.location',
        string='Location',
        required=True,
        tracking=True)

    current_quantity = fields.Float(
        string='Current Quantity',
        related='location_id.product_quantity',
        readonly=True)

    minimum_quantity = fields.Float(
        string='Minimum Quantity',
        required=True,
        tracking=True)

    maximum_quantity = fields.Float(
        string='Maximum Quantity',
        required=True,
        tracking=True)

    reorder_quantity = fields.Float(
        string='Reorder Quantity',
        compute='_compute_reorder_quantity',
        store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], default='draft', string='Status', tracking=True)

    alert_type = fields.Selection([
        ('minimum', 'Minimum Quantity Alert'),
        ('maximum', 'Maximum Quantity Alert')
    ], compute='_compute_alert_type', store=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('inventory.reorder.alert') or 'New'
        return super(ReorderAlert, self).create(vals)

    @api.depends('current_quantity', 'minimum_quantity', 'maximum_quantity')
    def _compute_alert_type(self):
        for alert in self:
            if alert.current_quantity < alert.minimum_quantity:
                alert.alert_type = 'minimum'
            elif alert.current_quantity > alert.maximum_quantity:
                alert.alert_type = 'maximum'
            else:
                alert.alert_type = False

    @api.depends('current_quantity', 'maximum_quantity')
    def _compute_reorder_quantity(self):
        for alert in self:
            if alert.current_quantity < alert.minimum_quantity:
                alert.reorder_quantity = alert.maximum_quantity - alert.current_quantity
            else:
                alert.reorder_quantity = 0.0

    @api.constrains('minimum_quantity', 'maximum_quantity')
    def _check_quantities(self):
        for alert in self:
            if alert.minimum_quantity >= alert.maximum_quantity:
                raise ValidationError(_('Maximum quantity must be greater than minimum quantity.'))
            if alert.minimum_quantity < 0 or alert.maximum_quantity < 0:
                raise ValidationError(_('Quantities cannot be negative.'))

    def action_activate(self):
        self.write({'state': 'active'})

    def action_deactivate(self):
        self.write({'state': 'inactive'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def check_reorder_points(self):
        """Cron job method to check reorder points and create activities"""
        alerts = self.search([('state', '=', 'active')])
        for alert in alerts:
            if alert.current_quantity < alert.minimum_quantity:
                self.env['mail.activity'].create({
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'note': _(f'Product {alert.product_id.name} needs reordering. Current quantity: {alert.current_quantity}'),
                    'user_id': self.env.user.id,
                    'res_id': alert.id,
                    'res_model_id': self.env['ir.model']._get('inventory.reorder.alert').id,
                })