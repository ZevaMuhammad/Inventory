from odoo import models, fields, api

class StockLocation(models.Model):
    _name = 'inventory.stock.location'
    _description = 'Stock Location'
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'parent_path'

    name = fields.Char(string='Location Name', required=True)
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name',
        store=True)
    parent_id = fields.Many2one(
        'inventory.stock.location', 'Parent Location',
        index=True, ondelete='cascade')
    child_ids = fields.One2many(
        'inventory.stock.location', 'parent_id',
        string='Child Locations')
    parent_path = fields.Char(index=True)
    
    warehouse_id = fields.Many2one(
        'inventory.warehouse',
        string='Warehouse',
        required=True)
    
    location_type = fields.Selection([
        ('internal', 'Internal Location'),
        ('incoming', 'Receiving'),
        ('outgoing', 'Shipping'),
        ('storage', 'Storage'),
        ('view', 'View'),
    ], string='Location Type', default='internal', required=True)
    
    active = fields.Boolean(default=True)
    
    product_ids = fields.Many2many(
        'inventory.product',
        'stock_location_product_rel',
        'location_id',
        'product_id',
        string='Products')
        
    product_quantity = fields.Float(
        string='Product Quantity',
        compute='_compute_product_quantity',
        store=True)
    
    stock_move_ids = fields.One2many(
        'inventory.stock.move',
        'location_id',
        string='Stock Moves')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for location in self:
            if location.parent_id:
                location.complete_name = '%s/%s' % (location.parent_id.complete_name, location.name)
            else:
                location.complete_name = location.name

    @api.depends('stock_move_ids.state', 'stock_move_ids.quantity')
    def _compute_product_quantity(self):
        for location in self:
            incoming = sum(location.stock_move_ids.filtered(
                lambda m: m.state == 'done' and m.destination_location_id == location).mapped('quantity'))
            outgoing = sum(location.stock_move_ids.filtered(
                lambda m: m.state == 'done' and m.source_location_id == location).mapped('quantity'))
            location.product_quantity = incoming - outgoing

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive location hierarchies.'))