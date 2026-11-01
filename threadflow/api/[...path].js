const crypto = require('node:crypto');
const { neon } = require('@neondatabase/serverless');
const { createInitialDatabase } = require('../src/data/seedData');

const username = (process.env.ADMIN_USERNAME || 'kamalakannan').trim().toLowerCase();
const password = process.env.ADMIN_PASSWORD || 'kamalhk';
const secret = process.env.AUTH_SESSION_SECRET;

function json(res, status, body, headers = {}) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  for (const [key, value] of Object.entries(headers)) res.setHeader(key, value);
  res.status(status).json(body);
}

function cookieMap(req) {
  return Object.fromEntries(String(req.headers.cookie || '').split(';').map(part => {
    const i = part.indexOf('=');
    return i < 0 ? [] : [part.slice(0, i).trim(), decodeURIComponent(part.slice(i + 1).trim())];
  }).filter(pair => pair.length === 2));
}

function sign(value) {
  return crypto.createHmac('sha256', secret).update(value).digest('hex');
}

function adminProfile(row = {}) {
  return {
    id: 'usr-admin', username, email: '', fullName: username, role: 'admin', department: 'Administration',
    avatarInitials: 'KK', themePreference: row.themePreference === 'dark' ? 'dark' : 'light',
    notifyDueSoon: row.notifyDueSoon !== false, notifyStatusChange: row.notifyStatusChange !== false,
    notifyCostingApproval: row.notifyCostingApproval !== false, active: true
  };
}

async function database() {
  if (!process.env.DATABASE_URL) throw new Error('DATABASE_URL is not configured.');
  if (!secret || secret.length < 32) throw new Error('AUTH_SESSION_SECRET must be at least 32 characters.');
  const sql = neon(process.env.DATABASE_URL);
  await sql`CREATE TABLE IF NOT EXISTS threadflow_state (id integer PRIMARY KEY CHECK (id = 1), data jsonb NOT NULL, updated_at timestamptz NOT NULL DEFAULT now())`;
  await sql`CREATE TABLE IF NOT EXISTS threadflow_sessions (token_hash text PRIMARY KEY, expires_at timestamptz NOT NULL)`;
  await sql`CREATE TABLE IF NOT EXISTS threadflow_login_attempts (ip text PRIMARY KEY, count integer NOT NULL, window_started_at timestamptz NOT NULL)`;
  const existing = await sql`SELECT 1 FROM threadflow_state WHERE id = 1`;
  if (!existing.length) {
    const seed = createInitialDatabase();
    seed.users = [adminProfile()];
    await sql`INSERT INTO threadflow_state (id, data) VALUES (1, ${JSON.stringify(seed)}::jsonb) ON CONFLICT (id) DO NOTHING`;
  }
  return sql;
}

async function sessionUser(req, sql) {
  const token = cookieMap(req).tf_session || '';
  const [id, signature] = token.split('.');
  if (!id || !signature || signature.length !== 64) return null;
  const expected = sign(id);
  if (!crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expected))) return null;
  const hash = crypto.createHash('sha256').update(id).digest('hex');
  const rows = await sql`SELECT 1 FROM threadflow_sessions WHERE token_hash = ${hash} AND expires_at > now()`;
  if (!rows.length) return null;
  const state = await sql`SELECT data->'users'->0 AS profile FROM threadflow_state WHERE id = 1`;
  return adminProfile(state[0]?.profile || {});
}

function checkSameOrigin(req) {
  const origin = req.headers.origin;
  if (origin && origin !== `https://${req.headers.host}` && origin !== `http://${req.headers.host}`) return false;
  return !req.headers['content-type'] || req.headers['content-type'].includes('application/json');
}

function cookieSecurity(req) {
  return /^(localhost|127\.0\.0\.1)(:\d+)?$/.test(req.headers.host || '') ? '' : '; Secure';
}

module.exports = async function handler(req, res) {
  try {
    if (!['GET', 'POST', 'PUT'].includes(req.method)) return json(res, 405, { error: 'Method not allowed.' }, { Allow: 'GET, POST, PUT' });
    if (req.method !== 'GET' && !checkSameOrigin(req)) return json(res, 403, { error: 'Request rejected.' });
    const sql = await database();
    const action = String(req.query.path || '').replace(/\/$/, '');

    if (action === 'session' && req.method === 'GET') return json(res, 200, { user: await sessionUser(req, sql) });

    if (action === 'login' && req.method === 'POST') {
      const ip = String(req.headers['x-forwarded-for'] || req.socket?.remoteAddress || 'unknown').split(',')[0].trim();
      const attempts = await sql`SELECT count, window_started_at FROM threadflow_login_attempts WHERE ip = ${ip}`;
      const attempt = attempts[0];
      if (attempt && Number(attempt.count) >= 10 && Date.now() - new Date(attempt.window_started_at).getTime() < 60_000) {
        return json(res, 429, { error: 'Too many sign in attempts. Try again in a minute.' }, { 'Retry-After': '60' });
      }
      const salt = crypto.createHash('sha256').update(secret).digest().subarray(0, 16);
      const candidate = crypto.scryptSync(String(req.body?.password || ''), salt, 64);
      const expected = crypto.scryptSync(password, salt, 64);
      const valid = String(req.body?.username || '').trim().toLowerCase() === username && crypto.timingSafeEqual(candidate, expected);
      if (!valid) {
        await sql`INSERT INTO threadflow_login_attempts (ip, count, window_started_at) VALUES (${ip}, 1, now()) ON CONFLICT (ip) DO UPDATE SET count = CASE WHEN threadflow_login_attempts.window_started_at < now() - interval '1 minute' THEN 1 ELSE threadflow_login_attempts.count + 1 END, window_started_at = CASE WHEN threadflow_login_attempts.window_started_at < now() - interval '1 minute' THEN now() ELSE threadflow_login_attempts.window_started_at END`;
        return json(res, 401, { error: 'Invalid username or password.' });
      }
      await sql`DELETE FROM threadflow_login_attempts WHERE ip = ${ip}`;
      const id = crypto.randomBytes(32).toString('hex');
      const hash = crypto.createHash('sha256').update(id).digest('hex');
      await sql`INSERT INTO threadflow_sessions (token_hash, expires_at) VALUES (${hash}, now() + interval '8 hours')`;
      const state = await sql`SELECT data->'users'->0 AS profile FROM threadflow_state WHERE id = 1`;
      return json(res, 200, { user: adminProfile(state[0]?.profile || {}) }, {
        'Set-Cookie': `tf_session=${id}.${sign(id)}; HttpOnly; SameSite=Strict; Path=/; Max-Age=28800${cookieSecurity(req)}`
      });
    }

    if (action === 'logout' && req.method === 'POST') {
      const token = (cookieMap(req).tf_session || '').split('.')[0];
      if (token) await sql`DELETE FROM threadflow_sessions WHERE token_hash = ${crypto.createHash('sha256').update(token).digest('hex')}`;
      return json(res, 200, { ok: true }, { 'Set-Cookie': `tf_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0${cookieSecurity(req)}` });
    }

    const user = await sessionUser(req, sql);
    if (!user) return json(res, 401, { error: 'Sign in required.' });
    if (action === 'database' && req.method === 'GET') {
      const rows = await sql`SELECT data FROM threadflow_state WHERE id = 1`;
      return json(res, 200, rows[0].data);
    }
    if (action === 'database' && req.method === 'PUT') {
      const data = req.body;
      if (!data || !Array.isArray(data.costingRecords) || !Array.isArray(data.orders) || !Array.isArray(data.tasks) || !Array.isArray(data.auditLogs)) return json(res, 400, { error: 'Invalid database snapshot.' });
      const old = await sql`SELECT data->'users'->0 AS profile FROM threadflow_state WHERE id = 1`;
      const profile = { ...adminProfile(old[0]?.profile || {}), themePreference: data.users?.[0]?.themePreference === 'dark' ? 'dark' : 'light', notifyDueSoon: data.users?.[0]?.notifyDueSoon !== false, notifyStatusChange: data.users?.[0]?.notifyStatusChange !== false, notifyCostingApproval: data.users?.[0]?.notifyCostingApproval !== false };
      data.users = [profile];
      await sql`UPDATE threadflow_state SET data = ${JSON.stringify(data)}::jsonb, updated_at = now() WHERE id = 1`;
      return json(res, 200, { ok: true });
    }
    return json(res, 404, { error: 'Not found.' });
  } catch (error) {
    console.error('ThreadFlow API error:', error.message);
    return json(res, 500, { error: 'The server could not complete this request.' });
  }
};
