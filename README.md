# Demo Odoo Project

Ushbu loyiha Odoo 17 manbasi va 2 ta custom moduldan iborat:

- `customer_credit_control`
- `sale_approval`

## 1) Talablar

- Python virtual environment (`venv`) tayyor bo'lishi
- PostgreSQL ishga tushgan bo'lishi
- Odoo DB user: `odoo`

## 2) Loyiha tuzilmasi

- Odoo manbasi: `odoo/`
- Custom modullar: `custom_addons/`
- Konfiguratsiya: `config/odoo.conf`

## 3) Konfiguratsiya

`config/odoo.conf` ichida asosiy sozlamalar:

- `db_host = 127.0.0.1`
- `db_port = 5432`
- `db_user = odoo`
- `db_password = odoo`
- `addons_path = /demo_odoo/odoo/addons,/demo_odoo/custom_addons`
- `http_port = 8069`

## 4) Ishga tushirish

```bash
cd /demo_odoo
source venv/bin/activate
python3 odoo/odoo-bin -c config/odoo.conf
```

Brauzerda:

- `http://localhost:8069`

## 5) Modullarni o'rnatish/yangilash

### Birinchi marta o'rnatish (`-i`)

```bash
python3 odoo/odoo-bin -c config/odoo.conf -d demo_tz -i customer_credit_control,sale_approval --stop-after-init
```

### O'zgartirishlardan keyin yangilash (`-u`)

```bash
python3 odoo/odoo-bin -c config/odoo.conf -d demo_tz -u customer_credit_control,sale_approval --stop-after-init
```

## 6) Loglarni ko'rish

Konfigda `logfile` yoqilgan bo'lsa:

```bash
tail -f /demo_odoo/odoo/odoo.log
```

## 7) Tez-tez uchraydigan xatolar

### `ModuleNotFoundError: No module named 'odoo.addons.web'`

Sabab: `addons_path` noto'g'ri.

To'g'ri qiymat:

```ini
addons_path = /demo_odoo/odoo/addons,/demo_odoo/custom_addons
```

Port tekshirish:

```bash
ss -ltnp | rg 8069
```
