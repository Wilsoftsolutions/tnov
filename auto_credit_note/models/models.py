# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InheritStockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super(InheritStockPicking, self).button_validate()
        if self.name.split('/')[1].upper() == 'RET':
            if self.sale_id:
                cr_note = self.sale_id._create_invoices(final=True)
                lines = self.env['sale.order.line'].search([('order_id', '=', self.sale_id.id)])
                product_ids = [line.product_id.id for line in lines]
                del_carr_p_id = [rec.product_id.id for rec in self.env['delivery.carrier'].search([])]
                ship_cost_p_id = list(set(product_ids) & set(del_carr_p_id))
                ship_cost_p_id = ship_cost_p_id[0] if ship_cost_p_id else ship_cost_p_id
                for rec in lines:
                    if rec.product_id.id == ship_cost_p_id:
                        cr_note.write({
                            'invoice_line_ids': [(0, 0, {
                                'product_id': ship_cost_p_id,
                                'price_unit': rec.price_unit,
                                'tax_ids': [(6, 0, rec.tax_id.ids)],
                                'discount': rec.discount
                            })]
                        })
                cr_note.action_post()
                related_invoice = self.env['account.move'].search([('invoice_origin', '=', cr_note.invoice_origin)])
                only_invoices = related_invoice.filtered(
                    lambda invoice: invoice.name.split('/')[0].upper() != "RINV" and invoice.payment_state in [
                        'not_paid', 'partial'])
                if only_invoices:
                    only_invoices = only_invoices[0] if only_invoices else only_invoices
                    move_lines = cr_note.line_ids.filtered(
                        lambda line: line.account_internal_type in ('receivable', 'payable') and not line.reconciled)
                    for line in move_lines:
                        only_invoices.js_assign_outstanding_line(line.id)
                    return res
                return res
            else:
                return res
        return res
