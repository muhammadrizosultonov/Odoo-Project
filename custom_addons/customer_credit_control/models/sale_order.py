from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    credit_limit_id = fields.Many2one(
        "customer.credit.limit",
        compute="_compute_credit_control_info",
        string="Credit Limit Record",
    )
    credit_limit_currency_id = fields.Many2one(
        "res.currency",
        compute="_compute_credit_control_info",
        string="Credit Currency",
    )
    remaining_credit = fields.Monetary(
        string="Remaining Credit",
        currency_field="credit_limit_currency_id",
        compute="_compute_credit_control_info",
    )
    is_credit_exceeded = fields.Boolean(
        string="Credit Exceeded",
        compute="_compute_credit_control_info",
    )

    @api.depends("partner_id", "amount_total", "currency_id")
    def _compute_credit_control_info(self):
        # Sale order ekrani uchun kredit limiti, qolgan kredit va oshib ketganlik flagini tayyorlaymiz.
        CreditLimit = self.env["customer.credit.limit"]
        for order in self:
            order.credit_limit_id = False
            order.credit_limit_currency_id = False
            order.remaining_credit = 0.0
            order.is_credit_exceeded = False

            if not order.partner_id:
                continue

            limit = CreditLimit.search([
                ("partner_id", "=", order.partner_id.commercial_partner_id.id),
                ("active", "=", True),
                ("company_id", "=", order.company_id.id),
            ], limit=1)
            if not limit:
                continue

            # Remaining credit va exceeded holatini real-time ko'rsatish uchun order summasini limit valyutasiga o'tkazamiz.
            order_amount_in_limit_currency = order.currency_id._convert(
                order.amount_total,
                limit.currency_id,
                order.company_id,
                order.date_order or fields.Date.context_today(order),
            )
            projected_total = limit.total_due + order_amount_in_limit_currency

            order.credit_limit_id = limit
            order.credit_limit_currency_id = limit.currency_id
            order.remaining_credit = limit.credit_limit - projected_total
            order.is_credit_exceeded = projected_total > limit.credit_limit

    def action_confirm(self):
        # Confirm paytida kredit limiti oshsa sale'ni bloklaymiz.
        for order in self:
            limit = self.env["customer.credit.limit"].search([
                ("partner_id", "=", order.partner_id.commercial_partner_id.id),
                ("active", "=", True),
                ("company_id", "=", order.company_id.id),
            ], limit=1)
            if not limit:
                continue
            limit._compute_due_and_remaining()

            order_amount_in_limit_currency = order.currency_id._convert(
                order.amount_total,
                limit.currency_id,
                order.company_id,
                order.date_order or fields.Date.context_today(order),
            )
            projected_total = limit.total_due + order_amount_in_limit_currency

            if projected_total > limit.credit_limit:
                raise ValidationError(
                    _(
                        "Credit limitdan oshib ketdi. Joriy qarz: %(due).2f %(cur)s, "
                        "Order: %(order).2f %(cur)s, Limit: %(limit).2f %(cur)s"
                    )
                    % {
                        "due": limit.total_due,
                        "order": order_amount_in_limit_currency,
                        "limit": limit.credit_limit,
                        "cur": limit.currency_id.name,
                    }
                )

        return super().action_confirm()
