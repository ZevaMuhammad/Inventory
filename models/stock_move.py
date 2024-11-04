from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class StockMove(models.Model):
    _name = 'inventory.stock.move'
    _description = 'Stock Move'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(
        'Reference',
        default='/',
        copy=False,
        required=True,
        readonly=True)

    date = fields.Datetime(
        'Date',
        default=fields.Datetime.now,
        tracking=True,
        required=True)

    product_id = fields.Many2one(
        'inventory.product',
        'Product',
        required=True,
        tracking=True,
        states={'done': [('readonly', True)]})

    quantity = fields.Float(
        'Quantity',
        required=True,
        tracking=True,
        states={'done': [('readonly', True)]})

    source_location_id = fields.Many2one(
        'inventory.stock.location',
        'Source Location',
        required=True,
        tracking=True,
        states={'done': [('readonly', True)]})

    destination_location_id = fields.Many2one(
        'inventory.stock.location',
        'Destination Location',
        required=True,
        tracking=True,
        states={'done': [('readonly', True)]})

    warehouse_id = fields.Many2one(
        'inventory.warehouse',
        'Warehouse',
        required=True,
        tracking=True,
        states={'done': [('readonly', True)]})

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    move_type = fields.Selection([
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
        ('internal', 'Internal')
    ], string='Move Type', compute='_compute_move_type', store=True)

    user_id = fields.Many2one(
        'res.users',
        'Responsible',
        default=lambda self: self.env.user,
        tracking=True)

    notes = fields.Text('Notes')

    @api.depends('source_location_id', 'destination_location_id')
    def _compute_move_type(self):
        for move in self:
            if move.source_location_id.location_type == 'incoming':
                move.move_type = 'incoming'
            elif move.destination_location_id.location_type == 'outgoing':
                move.move_type = 'outgoing'
            else:
                move.move_type = 'internal'

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('inventory.stock.move')
        return super(StockMove, self).create(vals)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        for move in self:
            if move.state != 'confirmed':
                raise ValidationError(_('Move must be confirmed before marking it as done.'))
            # Check if source location has enough quantity
            if move.move_type == 'outgoing' or move.move_type == 'internal':
                available_qty = move.source_location_id.product_quantity
                if available_qty < move.quantity:
                    raise ValidationError(_(
                        'Not enough quantity available in %s. Available: %s, Required: %s'
                    ) % (move.source_location_id.name, available_qty, move.quantity))
        self.write({'state': 'done'})

    def action_cancel(self):
        if any(move.state == 'done' for move in self):
            raise ValidationError(_('Cannot cancel a done move'))
        self.write({'state': 'cancelled'})

    def action_draft(self):
        if any(move.state == 'done' for move in self):
            raise ValidationError(_('Cannot reset a done move'))
        self.write({'state': 'draft'})

    @api.constrains('source_location_id', 'destination_location_id')
    def _check_locations(self):
        for move in self:
            if move.source_location_id == move.destination_location_id:
                raise ValidationError(_('Source and destination locations cannot be the same.'))