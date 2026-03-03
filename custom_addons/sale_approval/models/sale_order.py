from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    approval_request_ids = fields.One2many("sale.approval.request", "sale_order_id", string="Approval Requests")
    approval_request_count = fields.Integer(compute="_compute_approval_request_count")
    is_approval_required = fields.Boolean(
        string="Approval Required",
        compute="_compute_is_approval_required",
    )

    @api.depends("approval_request_ids")
    def _compute_approval_request_count(self):
        # Smart button uchun requestlar sonini hisoblaymiz.
        for order in self:
            order.approval_request_count = len(order.approval_request_ids)

    @api.depends("amount_total", "currency_id", "company_id")
    def _compute_is_approval_required(self):
        # 10,000 company currencydan yuqori buyurtmalarga approval talab qilamiz.
        threshold = 10000.0
        for order in self:
            amount_in_company_currency = order.currency_id._convert(
                order.amount_total,
                order.company_id.currency_id,
                order.company_id,
                order.date_order or fields.Date.context_today(order),
            )
            order.is_approval_required = amount_in_company_currency > threshold

    def _get_latest_approved_request(self):
        # Shu order uchun oxirgi approve bo'lgan requestni topamiz.
        self.ensure_one()
        approved_requests = self.approval_request_ids.filtered(lambda r: r.state == "approved")
        if not approved_requests:
            return self.env["sale.approval.request"]
        return approved_requests.sorted("id", reverse=True)[:1]

    def action_confirm(self):
        # Confirmdan oldin thresholddan katta orderlarda approval mavjudligini tekshiramiz.
        if self.env.context.get("skip_approval_check"):
            return super().action_confirm()

        threshold = 10000.0
        for order in self:
            amount_in_company_currency = order.currency_id._convert(
                order.amount_total,
                order.company_id.currency_id,
                order.company_id,
                order.date_order or fields.Date.context_today(order),
            )

            if amount_in_company_currency <= threshold:
                continue

            approved_request = order._get_latest_approved_request()
            if approved_request:
                continue

            # Oldin pending request bo'lmasa yangi request ochamiz.
            pending_request = order.approval_request_ids.filtered(lambda r: r.state in ("draft", "submitted"))[:1]
            if not pending_request:
                self.env["sale.approval.request"].create({
                    "sale_order_id": order.id,
                    "requested_by": self.env.user.id,
                    "state": "draft",
                })

            raise UserError(_("Approval required: ushbu orderni tasdiqlash uchun avval manager approval kerak."))

        return super().action_confirm()

    def action_view_approval_requests(self):
        # Smart button bosilganda shu orderga tegishli requestlarni tree/formda ochamiz.
        self.ensure_one()
        action = self.env.ref("sale_approval.action_sale_approval_request").read()[0]
        action["domain"] = [("sale_order_id", "=", self.id)]
        action["context"] = {
            "default_sale_order_id": self.id,
            "default_requested_by": self.env.user.id,
        }
        return action
