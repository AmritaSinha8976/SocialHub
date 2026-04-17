# SocialHub 🌐

A full-featured, production-ready social media web application built with **Django**, **Bootstrap 5**, and **vanilla JavaScript**. Includes a complete **REST API** for mobile apps. Designed as a portfolio-grade project that can be deployed immediately.

**🔗 Live Demo:** [https://socialhub-vwmf.onrender.com](https://socialhub-vwmf.onrender.com)

---

## ✨ Features

### Web Application
| Feature | Details |
|---|---|
| **Auth** | OTP-based email verification, secure password hashing |
| **Profiles** | Profile picture, bio, website, location, private accounts, themes |
| **Follow system** | Follow / unfollow, follow requests for private accounts |
| **Posts** | Create posts (image + caption), delete, save/bookmark posts |
| **Likes** | Like / unlike posts — AJAX, no page reload, duplicate-proof |
| **Comments** | Add / delete comments — AJAX inline on feed + detail view |
| **Feed** | Posts from followed users in reverse chronological order |
| **Explore** | Discover all posts from the community |
| **Stories** | 24-hour stories with text overlays, filters, stickers, polls, music metadata |
| **Chat** | Request-gated one-to-one messaging with real-time updates |
| **Notifications** | In-app notifications for likes, comments, follows, chat requests |
| **Block** | Block/unblock users to prevent interactions |
| **Search** | Find users by username |
| **Admin** | Full Django admin for all models |

### REST API (Mobile Ready)
| Feature | Details |
|---|---|
| **Authentication** | JWT-based auth with refresh tokens, OTP verification |
| **Full CRUD** | All web features available via REST endpoints |
| **Pagination** | Efficient data loading for mobile apps |
| **CORS** | Configured for React Native / Flutter apps |
| **Documentation** | Clean, RESTful endpoints at `/api/v1/` |

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
│   │   └── production.py       # PostgreSQL, Cloudinary, HTTPS
│   ├── urls.py
│   └── wsgi.py
│
├── users/                      # Authentication & profiles app
│   ├── models.py               # Profile, Follow, FollowRequest, Block, OTPVerification
│   ├── views.py                # register, login, profile, follow, block, search
│   ├── forms.py                # RegistrationForm, LoginForm, ProfileUpdateForm
│   ├── urls.py
│   ├── signals.py              # Auto-create Profile on User creation
│   ├── context_processors.py   # Global context (theme, notifications)
│   ├── admin.py
│   └── templatetags/
│       └── user_tags.py        # Custom template filters
│
├── posts/                      # Posts, likes, comments, saved posts
│   ├── models.py               # Post, Like, Comment, SavedPost
│   ├── views.py                # feed, create, detail, like, comment, save, delete
│   ├── forms.py                # PostForm, CommentForm
│   ├── urls.py
│   └── admin.py
│
├── stories/                    # Instagram-like 24h stories
│   ├── models.py               # Story, StoryView, StoryLike, StoryPollVote
│   ├── views.py                # create, view, delete, like, vote
│   ├── forms.py                # StoryForm
│   ├── urls.py
│   └── admin.py
│
├── chat/                       # One-to-one messaging
│   ├── models.py               # ChatRequest, ChatRoom, Message
│   ├── views.py                # inbox, room, send, accept/reject requests
│   ├── forms.py                # MessageForm
│   ├── urls.py
│   └── admin.py
│
├── notifications/              # In-app notifications
│   ├── models.py               # Notification
│   ├── views.py                # list, mark as read
│   ├── urls.py
│   └── admin.py
│
├── api/                        # REST API for mobile apps
│   ├── views.py                # All API endpoints (JWT auth)
│   ├── serializers.py          # DRF serializers
│   ├── urls.py                 # API URL patterns
│   └── apps.py
│
├── templates/
│   ├── base.html               # Master layout (navbar, messages, theme)
│   ├── users/
│   │   ├── login.html
│   │   ├── register_step1.html, register_step2.html, register_step3.html
│   │   ├── profile.html
│   │   ├── edit_profile.html
│   │   ├── follow_requests.html
│   │   ├── blocked_list.html
│   │   └── search.html
│   ├── posts/
│   │   ├── feed.html
│   │   ├── post_detail.html
│   │   ├── create_post.html
│   │   ├── saved_posts.html
│   │   ├── confirm_delete.html
│   │   └── explore.html
│   ├── stories/
│   │   ├── create_story.html
│   │   └── view_story.html
│   ├── chat/
│   │   ├── inbox.html
│   │   └── room.html
│   ├── notifications/
│   │   └── list.html
│   └── partials/
│       ├── post_card.html      # Reusable post card component
│       └── sidebar_user.html   # Reusable sidebar component
│
├── static/
│   ├── css/main.css            # Full custom stylesheet with theme support
│   ├── js/main.js              # AJAX likes, comments, follow, theme toggle
│   └── images/                 # Static assets
│
└── media/                      # User-uploaded files (Cloudinary in production)
    ├── profile_pics/
    ├── posts/
    └── stories/
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

### Web Application
| URL | View |
|---|---|
| `/` | Feed (login required) |
| `/explore/` | Explore all posts |
| `/post/new/` | Create a post |
| `/post/<id>/` | Post detail |
| `/posts/saved/` | Saved/bookmarked posts |
| `/profile/<username>/` | User profile |
| `/profile/edit/me/` | Edit your profile |
| `/follow/<username>/` | Follow / unfollow (POST) |
| `/follow-requests/` | Pending follow requests |
| `/blocked-users/` | Blocked users list |
| `/stories/` | Stories feed |
| `/stories/create/` | Create a story |
| `/stories/<id>/` | View story |
| `/chat/` | Chat inbox |
| `/chat/<room_id>/` | Chat room |
| `/notifications/` | Notifications list |
| `/search/` | Search users |
| `/register/` | Register (3-step OTP flow) |
| `/login/` | Login |
| `/logout/` | Logout |
| `/admin/` | Django admin panel |

### REST API
| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/auth/otp/request/` | POST | Request OTP for registration |
| `/api/v1/auth/otp/verify/` | POST | Verify OTP code |
| `/api/v1/auth/set-password/` | POST | Set password & create account |
| `/api/v1/auth/login/` | POST | Login (returns JWT tokens) |
| `/api/v1/auth/logout/` | POST | Logout (blacklist refresh token) |
| `/api/v1/auth/me/` | GET | Get current user profile |
| `/api/v1/posts/feed/` | GET | Get feed posts (paginated) |
| `/api/v1/posts/explore/` | GET | Get explore posts (paginated) |
| `/api/v1/posts/create/` | POST | Create a new post |
| `/api/v1/posts/<id>/` | GET | Get post detail |
| `/api/v1/posts/<id>/like/` | POST | Toggle like on post |
| `/api/v1/posts/<id>/save/` | POST | Toggle save/bookmark post |
| `/api/v1/posts/<id>/comment/` | POST | Add comment to post |
| `/api/v1/stories/` | GET | Get stories feed |
| `/api/v1/stories/create/` | POST | Create a story |
| `/api/v1/chat/` | GET | Get chat inbox |
| `/api/v1/chat/<room_id>/` | GET/POST | Get messages / send message |
| `/api/v1/notifications/` | GET | Get notifications |
| `/api/v1/users/search/` | GET | Search users |
| `/api/v1/users/<username>/` | GET | Get user profile |
| `/api/v1/users/<username>/follow/` | POST | Toggle follow |
| `/api/v1/users/<username>/block/` | POST | Toggle block |

---

## ☁️ Deployment

### Option A — Render (Recommended, Free Tier)

Render is the easiest platform. The `render.yaml` in this repo handles everything automatically.

**Steps:**
1. Push your code to GitHub.
2. Go to [render.com](https://render.com) → New → Blueprint.
3. Connect your GitHub repo.
4. Render reads `render.yaml` and sets up the web service + PostgreSQL database.
5. Add environment variables in the Environment tab:
   - `SECRET_KEY` (auto-generated or use: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
   - `CLOUDINARY_CLOUD_NAME` (from [cloudinary.com](https://cloudinary.com))
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`
6. Click **Deploy**. Done.

**Note:** Render's free tier has ephemeral storage, so **Cloudinary is required** for persistent media storage (profile pictures, posts, stories).

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
| API | Django REST Framework, JWT Authentication |
| Frontend | HTML5, CSS3, Bootstrap 5, Vanilla JS |
| Fonts | Playfair Display, DM Sans (Google Fonts) |
| Icons | Bootstrap Icons |
| Static files | WhiteNoise |
| Media storage | Cloudinary (production) |
| WSGI server | Gunicorn |
| Reverse proxy | Nginx |
| Image handling | Pillow |
| Email | SMTP (OTP verification) |
| CORS | django-cors-headers (for mobile apps) |

---

## 🧩 Data Models

```
User (Django built-in)
 └── Profile (OneToOne)
      - profile_picture, bio, website, location
      - is_private (private account)
      - theme (light/dark)

OTPVerification
 - email, otp, username, first_name, last_name
 - expires_at, is_verified

Follow
 - follower → User
 - following → User
 (unique_together prevents duplicate follows)

FollowRequest
 - sender → User
 - receiver → User
 - status (pending/accepted/rejected)

Block
 - blocker → User
 - blocked → User

Post
 - author → User
 - image (optional), caption (optional)
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

SavedPost
 - user → User
 - post → Post
 (bookmarked posts)

Story
 - author → User
 - image, caption, text_color, text_size, text_align, text_style
 - bg_color, bg_gradient, filter_name
 - stickers_json (JSON array)
 - music_title, music_artist
 - poll_question, poll_option_a, poll_option_b
 - expires_at (24 hours)

StoryView
 - story → Story
 - viewer → User

StoryLike
 - story → Story
 - user → User

StoryPollVote
 - story → Story
 - user → User
 - choice (a/b)

ChatRequest
 - sender → User
 - receiver → User
 - status (pending/accepted/rejected)

ChatRoom
 - user1 → User
 - user2 → User
 (one-to-one messaging)

Message
 - room → ChatRoom
 - sender → User
 - text, is_read

Notification
 - recipient → User
 - actor → User
 - notif_type (follow_request, follow_accepted, chat_request, etc.)
 - message, url, is_read
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
