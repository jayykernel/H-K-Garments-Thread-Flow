# ThreadFlow on Vercel

ThreadFlow is a single-admin production tracking app. The static UI is served from `dist/threadflow.html`; `api/login.js`, `api/session.js`, `api/logout.js`, and `api/database.js` implement its Vercel endpoints. Records and sessions are stored in Neon Postgres. No local SQLite file is used.

## Deploy

1. Push this folder to a GitHub repository.
2. In Vercel, create a project and import the repository. Leave the build command and output directory at their defaults; the checked-in HTML and API function are ready to deploy.
3. Create a Neon Postgres database (from Vercel Marketplace or Neon) and copy its pooled connection string.
4. In Vercel Project → Settings → Environment Variables, add `DATABASE_URL`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, and `AUTH_SESSION_SECRET` for Production (and Preview if needed). Use `kamalakannan` and `kamalhk` for the requested initial login. Generate a private random session secret of at least 32 characters.
5. Redeploy after saving environment variables. Open the deployment URL, sign in, create a record, then sign out/in to confirm it persisted.

The database tables and initial sample dataset are created automatically on first API use. Only the single `kamalakannan` administrator can sign in; there is no registration or role switching. The initial `kamalhk` password is weak for a public site, so replace it with a long unique password in Vercel before sharing the URL.

## Local development

Use Node.js 22 or newer, set the variables from `.env.example` in a local `.env` file, then run `npm install` and `npx vercel dev`. Vercel's local development command reads `.env` and serves the same function routes.

## Notes

- `db/001_initial_schema.sql` is a reference schema; the current runtime creates its own compact JSONB state and session tables in Neon.
- App database export is available in Settings. Neon also provides database backup and restore options.
- Run `python build_app.py` after changing the HTML template or embedded engines to refresh `dist/threadflow.html`.
