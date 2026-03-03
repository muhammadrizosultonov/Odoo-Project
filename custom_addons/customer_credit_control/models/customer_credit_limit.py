from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CustomerCreditLimit(models.Model):
    _name = "customer.credit.limit"
    _description = "Customer Credit Limit"
    _rec_name = "partner_id"

    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
        domain=[("customer_rank", ">", 0)],
    )
    credit_limit = fields.Monetary(string="Credit Limit", required=True)
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id.id,
    )
    active = fields.Boolean(default=True)
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company.id,
    )
    total_due = fields.Monetary(
        string="Total Due",
        compute="_compute_due_and_remaining",
        store=True,
    )
    remaining_credit = fields.Monetary(
        string="Remaining Credit",
        compute="_compute_due_and_remaining",
        store=True,
    )

    _sql_constraints = [
        (
            "check_credit_limit_positive",
            "CHECK(credit_limit >= 0)",
            "Credit limit manfiy bo'lishi mumkin emas.",
        ),
    ]

    @api.depends("partner_id", "credit_limit", "currency_id", "company_id")
    def _compute_due_and_remaining(self):
        # Bu compute ichida mijozning posted va to'liq to'lanmagan invoice qoldiqlarini yig'amiz.
        for rec in self:
            total_due = 0.0
            if rec.partner_id:
                commercial_partner = rec.partner_id.commercial_partner_id
                invoices = self.env["account.move"].search([
                    ("move_type", "in", ("out_invoice", "out_refund")),
                    ("state", "=", "posted"),
                    ("payment_state", "!=", "paid"),
                    ("commercial_partner_id", "=", commercial_partner.id),
                    ("company_id", "=", rec.company_id.id),
                ])
                for inv in invoices:
                    # amount_residual_signed invoice kompaniyasi valyutasida bo'ladi, shuni limit valyutasiga o'tkazamiz.
                    total_due += inv.company_id.currency_id._convert(
                        inv.amount_residual_signed,
                        rec.currency_id,
                        rec.company_id,
                        inv.invoice_date or fields.Date.context_today(rec),
                    )
            rec.total_due = total_due
            # Bu yerda qolgan kreditni oddiy formula bilan hisoblayapmiz.
            rec.remaining_credit = rec.credit_limit - rec.total_due

    @api.constrains("partner_id", "active")
    def _check_only_one_active_limit_per_partner(self):
        # Bitta mijoz uchun bitta aktiv kredit limiti bo'lishi kerak, aks holda xatolik beramiz.
        for rec in self.filtered(lambda r: r.active and r.partner_id):
            duplicate = self.search([
                ("id", "!=", rec.id),
                ("active", "=", True),
                ("partner_id", "=", rec.partner_id.id),
            ], limit=1)
            if duplicate:
                raise ValidationError(
                    _("Har bir mijoz uchun faqat bitta active credit limit bo'lishi mumkin.")
                )
