from odoo import models, api

class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    @api.depends('company_id', 'location_id', 'owner_id', 'product_id', 'quantity')
    def _compute_value(self):
        super(StockQuant, self)._compute_value()
        for record in self:
            if record.product_id.cost_level == 'lot':
                svls = self.env['stock.valuation.layer'].sudo().search([('product_id','=', record.product_id.id), ('company_id','=', record.company_id.id),('lot_id','=', record.lot_id.id), ('remaining_qty','>',0)])
                total_value = 0
                total_qty = 0
                for svl in svls:
                    total_value += svl.remaining_value
                    total_qty += svl.remaining_qty
                unit_value = total_qty and total_value / total_qty or 0
                record.value = unit_value * record.quantity