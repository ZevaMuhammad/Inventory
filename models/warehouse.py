from odoo import models, fields, api

class Warehouse(models.Model):
    _name = 'inventory.warehouse'
    _description = 'Warehouse'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Warehouse Name', required=True, tracking=True)
    code = fields.Char(string='Warehouse Code', required=True, tracking=True)
    address = fields.Text(string='Address')
    manager_id = fields.Many2one('res.users', string='Warehouse Manager')
    active = fields.Boolean(default=True)

    location_ids = fields.One2many('inventory.stock.location', 'warehouse_id', string='Stock Locations')
    stock_move_ids = fields.One2many('inventory.stock.move', 'warehouse_id', string='Stock Moves')

    total_product_quantity = fields.Float(string='Total Product Quantity', compute='_compute_total_quantity')
    product_count = fields.Integer(string='Number of Products', compute='_compute_product_count')

    @api.depends('location_ids.product_quantity')
    def _compute_total_quantity(self):
        for warehouse in self:
            warehouse.total_product_quantity = sum(warehouse.location_ids.mapped('product_quantity'))

    @api.depends('location_ids.product_ids')
    def _compute_product_count(self):
        for warehouse in self:
            products = self.env['inventory.product'].search([('id', 'in', warehouse.location_ids.mapped('product_ids').ids)])
            warehouse.product_count = len(products)

    def action_view_products(self):
        self.ensure_one()
        products = self.env['inventory.product'].search([('id', 'in', self.location_ids.mapped('product_ids').ids)])
        action = self.env.ref('inventory.action_inventory_product').read()[0]
        action['domain'] = [('id', 'in', products.ids)]
        return action