from odoo import models, fields, api
from odoo.tools.float_utils import float_is_zero, float_compare, float_round

class StockMove(models.Model):
    _inherit = "stock.move"
    
    lot_id = fields.Many2one('stock.lot', 'Lot/Serial Number', compute = '_calc_lot_id', store = True)
    
    @api.depends('move_line_ids.lot_id')
    def _calc_lot_id(self):
        for record in self:
            lot_id = record.mapped('move_line_ids.lot_id')
            record.lot_id = len(lot_id) ==1 and lot_id
    
    def _prepare_common_svl_vals(self):
        vals = super(StockMove, self)._prepare_common_svl_vals()
        if self.product_id.cost_level == 'lot' and len(self.move_line_ids.lot_id) == 1:
            vals.update({
                'lot_id' : self.move_line_ids.lot_id.id
                })
        return vals
    
    def _create_out_svl(self, forced_quantity=None):
        move_ids = self.filtered(lambda move : move.product_id.cost_level == 'lot')
        svl_ids = super(StockMove, self - move_ids)._create_out_svl(forced_quantity = forced_quantity)
        svl_ids += move_ids._create_out_svl_lot(forced_quantity = forced_quantity)
        return svl_ids
    

    def _create_out_svl_lot(self, forced_quantity=None):
        """Create a `stock.valuation.layer` from `self`.

        :param forced_quantity: under some circunstances, the quantity to value is different than
            the initial demand of the move (Default value = None)
        """
        svl_vals_list = []
        for move in self:
            move = move.with_company(move.company_id)
            valued_move_lines = move._get_out_move_lines()
            
            
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, move.product_id.uom_id)
            if float_is_zero(forced_quantity or valued_quantity, precision_rounding=move.product_id.uom_id.rounding):
                continue            
            svl_vals = move.product_id._prepare_out_svl_vals_lot(forced_quantity or valued_quantity, move.company_id, move.lot_id)
            svl_vals.update(move._prepare_common_svl_vals())
            if forced_quantity:
                svl_vals['description'] = 'Correction of %s (modification of past move)' % move.picking_id.name or move.name
            svl_vals['description'] += svl_vals.pop('rounding_adjustment', '')
            svl_vals_list.append(svl_vals)
        return self.env['stock.valuation.layer'].sudo().create(svl_vals_list)

    def _register_hook(self):
        super(StockMove, self)._register_hook()

        def _get_price_unit(self):
            """ Returns the unit price for the move"""
            self.ensure_one()
            if self.origin_returned_move_id or not self.purchase_line_id or not self.product_id.id:
                return _get_price_unit.origin(self)
            price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')
            line = self.purchase_line_id
            order = line.order_id
            received_qty = line.qty_received
            if self.state == 'done':
                quantity_done = sum(self.picking_id.move_ids.filtered(lambda move:move.product_id == self.product_id).mapped('quantity_done'))
                received_qty -= self.product_uom._compute_quantity(quantity_done, line.product_uom, rounding_method='HALF-UP')
                
            if float_compare(line.qty_invoiced, received_qty, precision_rounding=line.product_uom.rounding) > 0:
                move_layer = line.move_ids.stock_valuation_layer_ids
                invoiced_layer = line.invoice_lines.stock_valuation_layer_ids
                receipt_value = sum(move_layer.mapped('value')) + sum(invoiced_layer.mapped('value'))
                invoiced_value = 0
                invoiced_qty = 0
                for invoice_line in line.invoice_lines:
                    if invoice_line.tax_ids:
                        invoiced_value += invoice_line.tax_ids.with_context(round=False).compute_all(
                            invoice_line.price_unit, currency=invoice_line.account_id.currency_id, quantity=invoice_line.quantity)['total_void']
                    else:
                        invoiced_value += invoice_line.price_unit * invoice_line.quantity
                    invoiced_qty += invoice_line.product_uom_id._compute_quantity(invoice_line.quantity, line.product_id.uom_id)
                # TODO currency check
                remaining_value = invoiced_value - receipt_value
                # TODO qty_received in product uom
                remaining_qty = invoiced_qty - line.product_uom._compute_quantity(received_qty, line.product_id.uom_id)
                price_unit = float_round(remaining_value / remaining_qty, precision_digits=price_unit_prec)
            else:
                price_unit = line.price_unit
                if line.taxes_id:
                    qty = line.product_qty or 1
                    price_unit = line.taxes_id.with_context(round=False).compute_all(price_unit, currency=line.order_id.currency_id, quantity=qty)['total_void']
                    price_unit = float_round(price_unit / qty, precision_digits=price_unit_prec)
                if line.product_uom.id != line.product_id.uom_id.id:
                    price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
            if order.currency_id != order.company_id.currency_id:
                # The date must be today, and not the date of the move since the move move is still
                # in assigned state. However, the move date is the scheduled date until move is
                # done, then date of actual move processing. See:
                # https://github.com/odoo/odoo/blob/2f789b6863407e63f90b3a2d4cc3be09815f7002/addons/stock/models/stock_move.py#L36
                price_unit = order.currency_id._convert(
                    price_unit, order.company_id.currency_id, order.company_id, fields.Date.context_today(self), round=False)
            return price_unit
        
        self._patch_method('_get_price_unit', _get_price_unit)
        