odoo.define('inventory_management.dashboard', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');

    var InventoryDashboard = Widget.extend({
        template: 'inventory_management.Dashboard',
        events: {
            'click .btn-refresh': '_onRefresh',
            'click .btn-generate-report': '_onGenerateReport',
        },

        init: function(parent, options) {
            this._super(parent);
            this.options = options || {};
        },

        start: function() {
            this._super.apply(this, arguments);
            this._updateDashboard();
        },

        _updateDashboard: function() {
            var self = this;
            this._rpc({
                model: 'inventory.product',
                method: 'get_dashboard_data',
                args: [],
            }).then(function(result) {
                self.$el.find('.total-products').text(result.total_products);
                self.$el.find('.low-stock-products').text(result.low_stock_products);
                // Update other dashboard elements
            });
        },

        _onRefresh: function(ev) {
            ev.preventDefault();
            this._updateDashboard();
        },

        _onGenerateReport: function(ev) {
            ev.preventDefault();
            // Implement report generation logic
            console.log('Generating report...');
        },
    });

    core.action_registry.add('inventory_dashboard', InventoryDashboard);

    return InventoryDashboard;
});