from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    lot_id = fields.Many2one('stock.lot', 'Lot/Serial Number')
    
    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('stock_move_id'):
                if not vals.get('lot_id') and self.env['product.product'].browse(vals['product_id']).cost_level == 'lot':
                    vals['lot_id'] = self.env['stock.move'].browse(vals['stock_move_id']).lot_id.id
        return super(StockValuationLayer, self).create(vals_list)
    
    #@api.constrains('lot_id', 'product_id')
    def _check_lot_id(self):
        for record in self:
            if record.product_id.cost_level == 'lot' and not record.lot_id:
                raise ValidationError(_('Missing required Lot/Serial Number'))
            