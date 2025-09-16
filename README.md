Name: M. Adra Prakoso
NPM: 2406453530
Class: PBP KKI

---

# Football Shop

Live (PWS): https://muhammad-adra41-footballshop.pbp.cs.ui.ac.id/

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
8. Deployment: added my PWS domain to `ALLOWED_HOSTS`.

## MVT in 3 lines
- `urls.py` picks the view based on the path.
- `views.py` gathers data and calls `render` with a context.
- `models.py` defines `Product` and lets me query without writing raw SQL.
- `main.html` uses the context to produce the final HTML.

## What `settings.py` does 
Project configuration lives here: installed apps, middleware, database settings, templates, static files, allowed hosts, debug flag, and so on. In this repo the database is always SQLite (local and PWS), and I listed the PWS domain in `ALLOWED_HOSTS` so it actually serves.

## How migrations work (quick)
1. Change models.
2. `makemigrations` creates migration files describing schema changes.
3. `migrate` applies them to the DB and records which ones ran.
That’s it. If you edit models again, repeat.

## Why Django for an intro course (my take)
- Comes with a lot of built-ins (admin, auth, ORM) so you can focus on concepts.
- Clear structure; easier to grade and to collaborate.
- Good docs and a stable ecosystem.
- Reasonably secure defaults (CSRF, etc.).

## Feedback for Tutorial 1
It was fine.

## Notes
- Local dev: DEBUG on, SQLite. Prod: still SQLite; domain is already in `ALLOWED_HOSTS`.
- The extra `News` model is unrelated to the assignment; I left it in for testing.

---

## Assignment Checklist

- DONE: 4 new view functions for data formats
- DONE: URL routes for each view
- DONE: Product list page with Add button and per-item Detail button
	- List: `/` (shows all products)
	- Add: `/add/`
	- Detail: `/product/<id>/`
- DONE: Form page to add product objects
- DONE: Detail page for each product
- DONE: Postman screenshots added: embedded below

### Postman Endpoints to Capture

Use these four GET endpoints in Postman, then add screenshots here:

1. All products XML: `https://muhammad-adra41-footballshop.pbp.cs.ui.ac.id/xml/`
2. All products JSON: `https://muhammad-adra41-footballshop.pbp.cs.ui.ac.id/json/`
3. Product by ID XML: `https://muhammad-adra41-footballshop.pbp.cs.ui.ac.id/xml/<id>/`
4. Product by ID JSON: `https://muhammad-adra41-footballshop.pbp.cs.ui.ac.id/json/<id>/`

Screenshots:

![Postman XML by ID](image-1758021027457.png)

![Postman XML (all)](image-1758021059639.png)

![Postman JSON by ID](image-1758021073647.png)

![Postman JSON (all)](image-1758021084252.png)

If you're running locally, the base is `http://127.0.0.1:8000/`.
