# SocialHub 🌐

A full-featured, production-ready social media web application built with **Django**, **Bootstrap 5**, and **vanilla JavaScript**. Designed as a portfolio-grade project that can be deployed immediately.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Auth** | Register, login, logout with secure password hashing |
| **Profiles** | Profile picture, bio, website, location, edit profile |
| **Follow system** | Follow / unfollow users, followers & following counts |
| **Posts** | Create posts (image + caption), delete posts, feed |
| **Likes** | Like / unlike posts — AJAX, no page reload, duplicate-proof |
| **Comments** | Add / delete comments — AJAX inline on feed + detail view |
| **Feed** | Posts from followed users in reverse chronological order |
| **Explore** | Discover all posts from the community |
| **Search** | Find users by username |
| **Admin** | Full Django admin for all models |

---

## 🏗 Project Structure

```
socialhub/
│
├── manage.py
├── requirements.txt
├── Procfile                    # Render / Railway / Heroku
├── render.yaml                 # One-click Render deployment
├── nginx.conf                  # Nginx config for VPS
├── socialhub.service           # systemd service for VPS
├── .env.example                # Copy to .env and fill in values
├── .gitignore
│
├── socialhub/                  # Django project package
│   ├── settings/
│   │   ├── __init__.py         # Auto-selects dev or prod
│   │   ├── base.py             # Shared settings
│   │   ├── development.py      # SQLite, DEBUG=True
│   │   └── production.py       # PostgreSQL, HTTPS, secure cookies
│   ├── urls.py
│   └── wsgi.py
│
├── users/                      # Authentication & profiles app
│   ├── models.py               # Profile, Follow
│   ├── views.py                # register, login, profile, follow, search
│   ├── forms.py                # RegistrationForm, LoginForm, ProfileUpdateForm
│   ├── urls.py
│   ├── signals.py              # Auto-create Profile on User creation
│   ├── admin.py
│   ├── templatetags/
│   │   └── user_tags.py        # Custom template filters
│   └── management/commands/
│       └── create_default_avatar.py
│
├── posts/                      # Posts, likes, comments app
│   ├── models.py               # Post, Like, Comment
│   ├── views.py                # feed, create, detail, like, comment, delete
│   ├── forms.py                # PostForm, CommentForm
│   ├── urls.py
│   └── admin.py
│
├── templates/
│   ├── base.html               # Master layout (navbar, messages)
│   ├── users/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── profile.html
│   │   ├── edit_profile.html
│   │   └── search.html
│   ├── posts/
│   │   ├── feed.html
│   │   ├── post_detail.html
│   │   ├── create_post.html
│   │   ├── confirm_delete.html
│   │   └── explore.html
│   └── partials/
│       ├── post_card.html      # Reusable post card component
│       └── sidebar_user.html   # Reusable sidebar component
│
├── static/
│   ├── css/main.css            # Full custom stylesheet (no Bootstrap overrides needed)
│   └── js/main.js              # AJAX likes, comments, follow toggle
│
└── media/                      # User-uploaded files (gitignored)
    └── profile_pics/
        └── default.png
```

---

## 🚀 Local Setup

### Prerequisites
- Python 3.10+
- pip
- (Optional) virtualenv

### 1 — Clone the repo

```bash
git clone https://github.com/yourusername/socialhub.git
cd socialhub
```

### 2 — Create a virtual environment

```bash
python -m venv venv

# Activate:
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### 4 — Set up environment variables

```bash
cp .env.example .env
# Open .env and set SECRET_KEY at minimum.
# Everything else works out of the box for development.
```

### 5 — Create the default avatar

```bash
python manage.py create_default_avatar
```

### 6 — Run migrations

```bash
python manage.py migrate
```

### 7 — Create a superuser (for admin panel)

```bash
python manage.py createsuperuser
```

### 8 — Run the dev server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000** — you're live! 🎉

Admin panel: **http://127.0.0.1:8000/admin**

---

## 🗄 Database

| Environment | Database |
|---|---|
| Development | SQLite (`db.sqlite3`) — zero config |
| Production | PostgreSQL — set `DATABASE_URL` env var |

---

## 📦 Key URLs

| URL | View |
|---|---|
| `/` | Feed (login required) |
| `/explore/` | Explore all posts |
| `/post/new/` | Create a post |
| `/post/<id>/` | Post detail |
| `/profile/<username>/` | User profile |
| `/profile/edit/me/` | Edit your profile |
| `/follow/<username>/` | Follow / unfollow (POST) |
| `/search/` | Search users |
| `/register/` | Register |
| `/login/` | Login |
| `/logout/` | Logout |
| `/admin/` | Django admin panel |

---

## ☁️ Deployment

### Option A — Render (Recommended, Free Tier)

Render is the easiest platform. The `render.yaml` in this repo handles everything automatically.

**Steps:**
1. Push your code to GitHub.
2. Go to [render.com](https://render.com) → New → Blueprint.
3. Connect your GitHub repo.
4. Render reads `render.yaml` and sets up the web service + PostgreSQL database.
5. Add your `SECRET_KEY` in the Environment tab (or let Render auto-generate it).
6. Click **Deploy**. Done.

---

### Option B — Railway

1. Push to GitHub.
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub Repo.
3. Add a **PostgreSQL** plugin.
4. Set environment variables:
   ```
   DJANGO_ENV=production
   SECRET_KEY=<generate one>
   ALLOWED_HOSTS=<your-app>.up.railway.app
   DATABASE_URL=<auto-filled by Railway plugin>
   ```
5. Set the start command to: `gunicorn socialhub.wsgi --log-file -`
6. Deploy.

---

### Option C — DigitalOcean / AWS VPS (Advanced)

Full control. Use this when you need custom domains, more compute, or want to learn server admin.

```bash
# 1. SSH into your server
ssh ubuntu@your-server-ip

# 2. Install dependencies
sudo apt update && sudo apt install python3-pip python3-venv nginx postgresql

# 3. Clone repo
git clone https://github.com/yourusername/socialhub.git
cd socialhub

# 4. Virtual environment
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 5. Set up PostgreSQL
sudo -u postgres psql
  CREATE DATABASE socialhub_db;
  CREATE USER socialhub_user WITH PASSWORD 'strongpassword';
  GRANT ALL PRIVILEGES ON DATABASE socialhub_db TO socialhub_user;
  \q

# 6. Configure .env
cp .env.example .env
nano .env
  # Set: DJANGO_ENV=production
  # Set: SECRET_KEY, ALLOWED_HOSTS, DATABASE_URL

# 7. Migrate, collect static, create avatar
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py create_default_avatar
python manage.py createsuperuser

# 8. Configure Nginx
sudo cp nginx.conf /etc/nginx/sites-available/socialhub
sudo ln -s /etc/nginx/sites-available/socialhub /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 9. Configure systemd service
sudo cp socialhub.service /etc/systemd/system/
sudo mkdir -p /var/log/socialhub
sudo systemctl daemon-reload
sudo systemctl enable socialhub
sudo systemctl start socialhub

# 10. SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## 🛡 Security Checklist (Production)

- [x] `SECRET_KEY` stored in `.env`, never hardcoded
- [x] `DEBUG=False` in production
- [x] `ALLOWED_HOSTS` set correctly
- [x] `SECURE_SSL_REDIRECT=True`
- [x] `SESSION_COOKIE_SECURE=True`
- [x] `CSRF_COOKIE_SECURE=True`
- [x] `SECURE_HSTS_SECONDS` set
- [x] Passwords hashed with Django's PBKDF2 (default)
- [x] CSRF protection on all POST forms
- [x] Login required on all sensitive views
- [x] Users can only delete their own posts/comments
- [x] No secrets in version control (`.gitignore`)

---

## 🎨 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Django 5.0 |
| Database | SQLite (dev), PostgreSQL (prod) |
| Frontend | HTML5, CSS3, Bootstrap 5, Vanilla JS |
| Fonts | Playfair Display, DM Sans (Google Fonts) |
| Icons | Bootstrap Icons |
| Static files | WhiteNoise |
| WSGI server | Gunicorn |
| Reverse proxy | Nginx |
| Image handling | Pillow |

---

## 🧩 Data Models

```
User (Django built-in)
 └── Profile (OneToOne)
      - profile_picture
      - bio, website, location

Follow
 - follower → User
 - following → User
 (unique_together prevents duplicate follows)

Post
 - author → User
 - image (optional)
 - caption (optional)
 - created_at

Like
 - user → User
 - post → Post
 (unique_together prevents duplicate likes)

Comment
 - post → Post
 - author → User
 - text
 - parent → Comment (self, for replies)
```

---

## 📸 Screenshots

> Register/Login → Feed → Profile → Create Post → Post Detail → Explore

The UI uses a warm terracotta accent (`#E8421A`) on a clean white/off-white base, with Playfair Display for the brand logotype and DM Sans for all body text. Card-based layout, fully mobile responsive.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, open an issue first to discuss what you'd like to change.

---

## 📄 License

MIT — free to use, modify, and deploy.

---

**Built with ❤️ using Django**
