from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _recompute_related_credit_limits(self):
        # Invoice o'zgarganda tegishli partnerlarning kredit limitini qayta hisoblaymiz.
        partners = self.mapped("commercial_partner_id")
        companies = self.mapped("company_id")
        if not partners:
            return
        limits = self.env["customer.credit.limit"].search([
            ("partner_id", "in", partners.ids),
            ("active", "=", True),
            ("company_id", "in", companies.ids),
        ])
        limits._compute_due_and_remaining()

    def write(self, vals):
        # To'lov holati, state yoki residualga ta'sir qiladigan write bo'lsa compute qayta yurishi kerak.
        res = super().write(vals)
        watched_keys = {"state", "payment_state", "amount_residual", "amount_residual_signed"}
        if watched_keys.intersection(vals.keys()):
            self._recompute_related_credit_limits()
        return res

    def action_post(self):
        # Invoice post bo'lganda ham kredit limit ma'lumotini yangilab qo'yamiz.
        res = super().action_post()
        self._recompute_related_credit_limits()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        moves._recompute_related_credit_limits()
        return moves

    def unlink(self):
        moves = self
        res = super().unlink()
        moves._recompute_related_credit_limits()
        return res
