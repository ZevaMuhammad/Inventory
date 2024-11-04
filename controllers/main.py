from odoo import http
from odoo.http import request


class InventoryController(http.Controller):
    @http.route('/inventory/dashboard', type='http', auth='user', website=True)
    def inventory_dashboard(self, **kwargs):
        """Render inventory dashboard"""
        values = {
            'products': request.env['inventory.product'].search([]),
            'locations': request.env['inventory.location'].search([]),
            'recent_movements': request.env['inventory.stock.movement'].search(
                [], limit=10, order='date desc'
            ),
            'low_stock_products': request.env['inventory.product'].search([
                ('quantity_available', '<=', 'reorder_point')
            ]),
        }
        return request.render('inventory_management.dashboard_template', values)

    @http.route('/inventory/product/<model("inventory.product"):product>', type='http', auth='user', website=True)
    def product_detail(self, product, **kwargs):
        """Display product detail page"""
        values = {
            'product': product,
            'movements': request.env['inventory.stock.movement'].search([
                ('product_id', '=', product.id)
            ], limit=20, order='date desc'),
        }
        return request.render('inventory_management.product_detail_template', values)

    @http.route('/inventory/report/generate', type='http', auth='user', website=True)
    def generate_report(self, **kwargs):
        """Generate and download inventory report"""
        report_type = kwargs.get('report_type', 'stock_level')
        if report_type == 'stock_level':
            return self._generate_stock_level_report()
        elif report_type == 'movement':
            return self._generate_movement_report()
        return request.redirect('/inventory/dashboard')

    def _generate_stock_level_report(self):
        """Generate stock level report"""
        # Implementation for stock level report generation
        products = request.env['inventory.product'].search([])
        # Add your report generation logic here
        return request.redirect('/inventory/dashboard')

    def _generate_movement_report(self):
        """Generate movement report"""
        # Implementation for movement report generation
        movements = request.env['inventory.stock.movement'].search([])
        # Add your report generation logic here
        return request.redirect('/inventory/dashboard')