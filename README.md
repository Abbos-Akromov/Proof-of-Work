# PoW — Proof of Work
**Premium video editor portfolio · Django 4.2 · Single-user**

---

## Rang sistemi (Color System)

### Premium Obsidian/Gold palette

| Nom         | Hex       | Ishlatilish joyi              |
|-------------|-----------|-------------------------------|
| Obsidian    | `#0D0D0D` | Dark mode background          |
| Surface     | `#141414` | Card, navbar background       |
| Surface-2   | `#1C1C1C` | Input fields, secondary cards |
| Gold        | `#C9A84C` | Logo P/W, accents, CTA        |
| Gold light  | `#E2C47A` | Hover state                   |
| Gold dark   | `#A07C2A` | Light mode gold               |
| Text        | `#F0EEE8` | Primary text (dark mode)      |
| Text muted  | `#888680` | Secondary text                |
| Border      | `#2A2A2A` | Subtle dividers               |

**Light mode counterparts:**
| Nom       | Hex       |
|-----------|-----------|
| bg        | `#F5F4F0` |
| surface   | `#FFFFFF` |
| border    | `#E0DED8` |

---

## Tezkor ishga tushirish

```bash
# 1. Virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Kutubxonalar
pip install -r requirements.txt

# 3. .env fayl
cp .env.example .env
# .env ichida SECRET_KEY ni o'zgartiring

# 4. Migratsiya
python manage.py migrate

# 5. Admin foydalanuvchi yaratish
python manage.py createsuperuser
# Username: admin (xohlagan isim)
# Email: (ixtiyoriy)
# Password: kuchli parol

# 6. Serverga tushirish
python manage.py runserver
```

Brauzerda: http://127.0.0.1:8000

---

## URL manzillar

| URL                        | Kim ko'ra oladi | Tavsif                         |
|----------------------------|-----------------|--------------------------------|
| `/`                        | Hammaga          | Bosh sahifa (Hero, About, Works)|
| `/brands/`                 | Hammaga          | Brandlar + ish turlari          |
| `/work/<id>/`              | Hammaga          | Ish namunasi detail sahifasi    |
| `/admin-panel/login/`      | Egasi            | Login sahifasi                  |
| `/admin-panel/`            | Egasi            | Dashboard (CRUD)                |
| `/admin-panel/profile/`    | Egasi            | Profilni tahrirlash             |
| `/admin-panel/brands/add/` | Egasi            | Brand qo'shish                  |
| `/django-admin/`           | Egasi            | Django standart admin           |

---

## Server (VPS) ga deploy qilish

### Nginx + Gunicorn (tavsiya etiladi)

```bash
# Production .env
DEBUG=False
SECRET_KEY=juda-kuchli-maxfiy-kalit-bu-yerga
ALLOWED_HOSTS=sizning-domen.uz,www.sizning-domen.uz

# Static fayllarni yig'ish
python manage.py collectstatic --noinput

# Gunicorn test
gunicorn pow.wsgi:application --bind 0.0.0.0:8000
```

**Nginx konfiguratsiyasi** (`/etc/nginx/sites-available/pow`):
```nginx
server {
    server_name sizning-domen.uz;

    location /media/ {
        alias /var/www/pow/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Alternativa: Railway / Render (eng oson)
1. GitHub ga push qiling
2. Railway.app yoki Render.com da "New Project" → GitHub repo
3. Environment variables ni kiriting
4. Deploy tugmasini bosing — tayyor!

---

## Loyiha tuzilmasi

```
pow/
├── manage.py
├── requirements.txt
├── .env.example
├── pow/                  # Django sozlamalari
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── portfolio/            # Asosiy ilova
│   ├── models.py         # Profile, Brand, CaseStudy
│   ├── views.py          # Public + Admin views
│   ├── urls.py
│   ├── forms.py
│   └── admin.py
├── templates/
│   ├── portfolio/        # Public sahifalar
│   └── admin_panel/      # Owner dashboard
├── static/
│   ├── css/main.css      # Barcha stillar
│   └── js/main.js        # Theme toggle, mobile menu
└── media/                # Upload bo'lgan fayllar
```

---

## Birinchi ishga tushirgandan keyin nima qilish

1. `/admin-panel/login/` → createsuperuser bilan kiring
2. `/admin-panel/profile/` → Ism, bio, ko'nikmalar, kontakt linklar kiriting
3. `/admin-panel/brands/add/` → Birinchi brandni qo'shing
   - **work_label** — logoning to'g'ridan-to'g'ri ostida ko'rsatiladigan aniq ish turi
4. `/admin-panel/works/add/` → Ish namunalarini qo'shing (YouTube havolasi)
5. Saytni ko'ring: `/`
