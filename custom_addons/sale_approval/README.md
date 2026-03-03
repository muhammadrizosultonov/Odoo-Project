# Sale Approval (Odoo 17)

## Qisqacha
Bu modul 10,000 company currencydan katta `sale.order` lar uchun approval request talab qiladi.

## O'rnatish va test (5-7 qadam)
1. `config/odoo.conf` ichida `addons_path` ga `custom_addons` kiritilganini tekshiring.
2. Apps'dan `Sale Approval` modulini install qiling.
3. Sales user bilan 10,000 dan kichik sale order yarating va `Confirm` qiling (approvalsiz o'tishi kerak).
4. Sales user bilan 10,000 dan katta sale order yarating va `Confirm` qiling (Approval required xatosi chiqishi kerak).
5. Sale order ichida `Approval` smart button orqali request ochilganini tekshiring.
6. Sales Manager bilan requestni `Submit` va `Approve` qiling.
7. Approve bo'lgandan keyin order avtomatik confirm bo'lganini tekshiring; reject holatda esa reason majburiy ekanini sinang.
