from odoo import models, fields, api, tools

class InventoryReport(models.Model):
    _name = 'inventory.report'
    _description = 'Inventory Report'
    _auto = False
    _order = 'date desc'

    date = fields.Datetime(string='Date', readonly=True)
    product_id = fields.Many2one('inventory.product', string='Product', readonly=True)
    warehouse_id = fields.Many2one('inventory.warehouse', string='Warehouse', readonly=True)
    location_id = fields.Many2one('inventory.stock.location', string='Location', readonly=True)
    quantity = fields.Float(string='Quantity', readonly=True)
    move_type = fields.Selection([
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
        ('internal', 'Internal')
    ], string='Move Type', readonly=True)
    user_id = fields.Many2one('res.users', string='User', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE or REPLACE VIEW %s as (
                SELECT
                    sm.id,
                    sm.date,
                    sm.product_id,
                    sm.warehouse_id,
                    sm.source_location_id as location_id,
                    sm.quantity,
                    sm.move_type,
                    sm.user_id
                FROM inventory_stock_move sm
                WHERE sm.state = 'done'
            )
        """ % self._table)

class ProductMovementReport(models.Model):
    _name = 'inventory.product.movement.report'
    _description = 'Product Movement Report'
    _auto = False

    product_id = fields.Many2one('inventory.product', string='Product', readonly=True)
    warehouse_id = fields.Many2one('inventory.warehouse', string='Warehouse', readonly=True)
    incoming_qty = fields.Float(string='Incoming', readonly=True)
    outgoing_qty = fields.Float(string='Outgoing', readonly=True)
    net_qty = fields.Float(string='Net Quantity', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE or REPLACE VIEW %s as (
                SELECT
                    min(sm.id) as id,
                    sm.product_id,
                    sm.warehouse_id,
                    sum(CASE WHEN sm.move_type = 'incoming' THEN sm.quantity ELSE 0 END) as incoming_qty,
                    sum(CASE WHEN sm.move_type = 'outgoing' THEN sm.quantity ELSE 0 END) as outgoing_qty,
                    sum(CASE 
                        WHEN sm.move_type = 'incoming' THEN sm.quantity 
                        WHEN sm.move_type = 'outgoing' THEN -sm.quantity 
                        ELSE 0 
                    END) as net_qty
                FROM inventory_stock_move sm
                WHERE sm.state = 'done'
                GROUP BY sm.product_id, sm.warehouse_id
            )
        """ % self._table)