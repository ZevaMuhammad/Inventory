from odoo import models, fields, api

class Product(models.Model):
    _name = 'inventory.product'
    _description = 'Product'
    
    name = fields.Char(string='Product Name', required=True)
    code = fields.Char(string='Product Code', required=True)
    category_id = fields.Many2one('inventory.product.category', string='Category')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    
    stock_location_ids = fields.Many2many(
        'inventory.stock.location',
        'product_stock_location_rel',
        'product_id',
        'location_id',
        string='Stock Locations')

    total_quantity = fields.Float(string='Total Quantity', compute='_compute_total_quantity', store=True)

    @api.depends('stock_location_ids.product_quantity')
    def _compute_total_quantity(self):
        for product in self:
            product.total_quantity = sum(product.stock_location_ids.mapped('product_quantity'))

    def action_view_stock_locations(self):
        self.ensure_one()
        action = self.env.ref('inventory.action_inventory_stock_location').read()[0]
        action['domain'] = [('id', 'in', self.stock_location_ids.ids)]
        return action