# Customer Credit Control (Odoo 17)

## Qisqacha
Bu modul mijoz uchun kredit limit saqlaydi va `sale.order` confirm paytida limit oshib ketishini bloklaydi.

## O'rnatish va test
1. `config/odoo.conf` ichida `addons_path` ga `custom_addons` ni qo'shing.
2. Odoo serverni ishga tushiring va Apps'da `Customer Credit Control` ni install qiling.
3. Accounting Manager user bilan `Credit Control -> Customer Credit Limits` dan mijoz uchun limit yarating.
4. Shu mijozga bir nechta customer invoice (`posted`, `unpaid`) yarating va qoldiq hosil qiling.
5. Sales user bilan sale order oching, formda `Remaining Credit` ko'rinishini tekshiring.
6. Limitdan kichik summa bilan `Confirm` qiling: muvaffaqiyatli o'tishi kerak.
7. Limitdan oshadigan summa bilan `Confirm` qiling: `ValidationError` chiqishi kerak.
