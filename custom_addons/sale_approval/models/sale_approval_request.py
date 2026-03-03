from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SaleApprovalRequest(models.Model):
    _name = "sale.approval.request"
    _description = "Sale Approval Request"
    _order = "id desc"

    name = fields.Char(
        string="Reference",
        default=lambda self: _("New"),
        readonly=True,
        copy=False,
    )
    sale_order_id = fields.Many2one("sale.order", required=True, ondelete="cascade")
    requested_by = fields.Many2one(
        "res.users",
        string="Requested By",
        default=lambda self: self.env.user,
        required=True,
        readonly=True,
    )
    approved_by = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
    )
    total_amount = fields.Monetary(
        string="Total Amount",
        compute="_compute_total_amount",
        store=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="sale_order_id.currency_id",
        store=True,
        readonly=True,
    )
    reject_reason = fields.Text(string="Reject Reason")

    @api.model_create_multi
    def create(self, vals_list):
        # Har bir approval request uchun ketma-ket unikal raqam beramiz.
        is_manager = self.env.user.has_group("sales_team.group_sale_manager")
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code("sale.approval.request") or _("New")
            if not is_manager:
                # Oddiy user requestni faqat draft holatda ochishi kerak.
                vals["state"] = "draft"
                vals["approved_by"] = False
                vals["requested_by"] = self.env.user.id
        return super().create(vals_list)

    def write(self, vals):
        # Security qatlamini faqat viewga qoldirmay, backend write'da ham qat'iy tekshiramiz.
        if not self.env.user.has_group("sales_team.group_sale_manager"):
            allowed_vals = {"state"}
            if set(vals.keys()) - allowed_vals:
                raise UserError(_("Oddiy user faqat requestni submit qila oladi."))
            if vals.get("state") != "submitted":
                raise UserError(_("Oddiy user faqat submitted holatga o'tkaza oladi."))
            invalid = self.filtered(lambda r: r.state != "draft" or r.requested_by != self.env.user)
            if invalid:
                raise UserError(_("Faqat o'zingiz yaratgan draft requestni submit qila olasiz."))
        return super().write(vals)

    @api.depends("sale_order_id", "sale_order_id.amount_total")
    def _compute_total_amount(self):
        # Request summasini sale order summasidan olib ko'rsatamiz.
        for rec in self:
            rec.total_amount = rec.sale_order_id.amount_total

    def action_submit(self):
        # Oddiy sales user draft holatdan submitted holatga o'tkaza oladi.
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Faqat draft holatdagi request submit qilinadi."))
            rec.state = "submitted"

    def action_approve(self):
        # Faqat Sales Manager approve qila oladi va keyin buyurtma avtomatik confirm qilinadi.
        if not self.env.user.has_group("sales_team.group_sale_manager"):
            raise UserError(_("Faqat Sales Manager approve qila oladi."))

        for rec in self:
            if rec.state not in ("submitted", "draft"):
                raise UserError(_("Faqat draft yoki submitted request approve qilinadi."))
            rec.write({
                "state": "approved",
                "approved_by": self.env.user.id,
                "reject_reason": False,
            })

            # Recursive chaqiriqni oldini olish uchun context flag bilan confirm qilamiz.
            if rec.sale_order_id.state in ("draft", "sent"):
                rec.sale_order_id.with_context(skip_approval_check=True).action_confirm()

    def action_reject(self):
        # Faqat Sales Manager reject qila oladi va sabab yozilishi shart.
        if not self.env.user.has_group("sales_team.group_sale_manager"):
            raise UserError(_("Faqat Sales Manager reject qila oladi."))

        for rec in self:
            if rec.state not in ("submitted", "draft"):
                raise UserError(_("Faqat draft yoki submitted request reject qilinadi."))
            if not rec.reject_reason:
                raise ValidationError(_("Reject qilish uchun reason kiritish majburiy."))
            rec.state = "rejected"
