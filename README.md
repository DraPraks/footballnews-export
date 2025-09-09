Name: M. Adra Prakoso
NPM: 2406453530
Class: PBP KKI

---

# Football Pro Shop

Live (PWS): https://muhammad-adra41-footballnews.pbp.cs.ui.ac.id/

This is a small Django app for the assignment. One project (`football_news`), one app (`main`), one `Product` model, a view that renders some personal info and product data, and a simple template. Deployed to PWS.

## What I did
1. `django-admin startproject football_news`.
2. `python manage.py startapp main`, then add `main` to `INSTALLED_APPS` in `settings.py`.
3. Wire URLs: in project `urls.py` include `main.urls`; in `main/urls.py` map `''` to `show_main`.
4. Make `Product` in `main/models.py` with these fields (as required):
	- name (CharField)
	- price (IntegerField)
	- description (TextField)
	- thumbnail (URLField)
	- category (CharField)
	- is_featured (BooleanField)
	I also added timestamps and some category choices. Not strictly needed, just convenient.
5. `makemigrations` and `migrate` so the table exists.
6. Basic view `show_main` returns `app_name`, my name/class, and a queryset of products to the template.
7. Template `main.html` prints the info and loops products.
8. Deployment: added my PWS domain to `ALLOWED_HOSTS`. For production I switch DB to PostgreSQL using env vars; locally it’s SQLite. Pushed and set env vars on PWS.

## MVT in 3 lines
In words:
- `urls.py` picks the view based on the path.
- `views.py` gathers data and calls `render` with a context.
- `models.py` defines `Product` and lets me query without writing raw SQL.
- `main.html` uses the context to produce the final HTML.

## What `settings.py` does (the stuff that makes Django work)
Project configuration lives here: installed apps, middleware, database settings, templates, static files, allowed hosts, debug flag, and so on. In this repo I read an env flag to choose SQLite locally and PostgreSQL on PWS, and I listed the PWS domain in `ALLOWED_HOSTS` so it actually serves.

## How migrations work (quick)
1. Change models.
2. `makemigrations` creates migration files describing schema changes.
3. `migrate` applies them to the DB and records which ones ran.
That’s it. If you edit models again, repeat.

## Why Django for an intro course (my take)
- Comes with a lot of built-ins (admin, auth, ORM) so you can focus on concepts, not plumbing.
- Clear structure; easier to grade and to collaborate.
- Good docs and a stable ecosystem.
- Reasonably secure defaults (CSRF, etc.).

## Feedback for Tutorial 1
It was fine. Maybe show a minimal admin customization (`list_display`) and a short note on using environment variables earlier.

## Notes
- Local dev: DEBUG on, SQLite. Prod: set env vars and use Postgres; domain is already in `ALLOWED_HOSTS`.
- The extra `News` model is unrelated to the assignment; I left it in for testing (or maybe I removed it can't remember).
- Gen AI (Grok) was used to assist in this assignment.
