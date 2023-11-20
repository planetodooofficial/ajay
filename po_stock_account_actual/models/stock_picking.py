from odoo import models

class Picking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        context = dict(self.env.context, do_not_unreserve = True, do_not_propagate = True, mail_notrack = True, tracking_disable = True)
        if self.picking_type_id.code != "internal":
            for move in self.with_context(tracking_disable = True).move_ids:
                move_line_ids = move.move_line_ids.filtered('qty_done')
                if move.product_id.cost_level == 'lot' and len(move_line_ids) > 1 and move.product_id.type == 'product':
                    line1_initial_demand = move.product_uom_qty
                    for move_line in move_line_ids[1:]:
                        if move_line.reserved_uom_qty or move_line.qty_done:
                            new_move = move.with_context(context).copy(default={
                                'product_uom_qty': move_line.qty_done,
                                'move_orig_ids': [(6, 0, move.move_orig_ids.ids)],
                                'move_dest_ids': [(6, 0, move.move_dest_ids.ids)]
                                })
                            move_line.with_context(context).write({
                              'move_id': new_move.id,
                              'reserved_uom_qty': move_line.qty_done
                            })
                            new_move.with_context(context)._action_confirm(merge=False)
                            line1_initial_demand -=  new_move.product_uom_qty
                        else:
                            move_line.with_context(context).write({'move_id': None, 'picking_id': None, 'state': 'draft'})
                        move.with_context(context).write({'product_uom_qty': line1_initial_demand})
        return super(Picking, self)._action_done()
    
    def _register_hook(self):
        super(Picking, self)._register_hook()
        Model = self.env.get('mrp.production')
        if Model is None:
            return
        
        def _post_inventory(self, cancel_backorder = False):
            context = dict(self.env.context, do_not_unreserve = True, do_not_propagate = True, mail_notrack = True, tracking_disable = True)
            for record in self:
                for move in record.with_context(tracking_disable = True).move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel')):
                    move_line_ids = move.move_line_ids.filtered('qty_done')
                    if move.product_id.cost_level == 'lot' and len(move_line_ids) > 1 and move.product_id.type == 'product':
                        line1_initial_demand = move.product_uom_qty
                        for move_line in move_line_ids[1:]:
                            if move_line.reserved_uom_qty or move_line.qty_done:
                                new_move = move.copy(default={
                                    'product_uom_qty': move_line.qty_done,
                                    'move_orig_ids': [(6, 0, move.move_orig_ids.ids)],
                                    'move_dest_ids': [(6, 0, move.move_dest_ids.ids)]
                                    })                            
                                move_line.write({
                                    'move_id': new_move.id,
                                    'reserved_uom_qty': move_line.qty_done
                                    })
                                new_move._action_confirm(merge=False)
                                line1_initial_demand -=  new_move.product_uom_qty
                            else:
                                move_line.write({'move_id': None, 'raw_material_production_id': None, 'state': 'draft'})
                        if move.product_uom_qty > move.quantity_done:
                            move.write({'product_uom_qty' : move.quantity_done})
                        move.with_context(context).write({'product_uom_qty': line1_initial_demand})
                        move._action_confirm(merge=False)
            return _post_inventory.origin(self, cancel_backorder = cancel_backorder)
        
        Model._patch_method('_post_inventory', _post_inventory)
        