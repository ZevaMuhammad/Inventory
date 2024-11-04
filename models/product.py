from odoo import models, fields, api

class Product(models.Model):
    _name = 'inventory.product'
    _description = 'Product'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Product Name', required=True, tracking=True)
    sku = fields.Char(string='SKU', required=True, tracking=True)
    barcode = fields.Char(string='Barcode')
    description = fields.Text(string='Description')
    category_id = fields.Many2one('inventory.product.category', string='Category')
    unit_of_measure = fields.Many2one('uom.uom', string='Unit of Measure')
    cost_price = fields.Float(string='Cost Price', digits=(10, 2), tracking=True)
    sale_price = fields.Float(string='Sale Price', digits=(10, 2), tracking=True)
    quantity_on_hand = fields.Float(string='Quantity on Hand', compute='_compute_quantity', store=True)
    reorder_point = fields.Float(string='Reorder Point')
    active = fields.Boolean(default=True)

    @api.depends('stock_move_ids')
    def _compute_quantity(self):
        for product in self:
            incoming = sum(product.stock_move_ids.filtered(lambda m: m.move_type == 'incoming').mapped('quantity'))
            outgoing = sum(product.stock_move_ids.filtered(lambda m: m.move_type == 'outgoing').mapped('quantity'))
            product.quantity_on_hand = incoming - outgoing

    stock_move_ids = fields.One2many('inventory.stock.move', 'product_id', string='Stock Moves')

class ProductCategory(models.Model):
    _name = 'inventory.product.category'
    _description = 'Product Category'

    name = fields.Char(string='Category Name', required=True)
    parent_id = fields.Many2one('inventory.product.category', string='Parent Category')
    child_ids = fields.One2many('inventory.product.category', 'parent_id', string='Child Categories')