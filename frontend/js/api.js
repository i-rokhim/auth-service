// api.js: pemanggilan API, header Authorization, dan penukaran refresh token.
// Bergantung pada auth.js (objek Auth), jadi dimuat sesudahnya.

const Api = (() => {
  const BASE_URL = 'http://localhost:8000/api/v1';

  async function readBody(response) {
    const text = await response.text();
    if (!text) {
      return null;
    }
    try {
      return JSON.parse(text);
    } catch {
      return null;
    }
  }

  // Satu kali kirim, tanpa logika ulang.
  function send(path, { method = 'GET', body, auth = true } = {}) {
    const headers = { 'Content-Type': 'application/json' };
    const access = Auth.getAccess();
    if (auth && access) {
      headers.Authorization = `Bearer ${access}`;
    }
    return fetch(BASE_URL + path, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  }

  async function exchangeRefreshToken() {
    const refresh = Auth.getRefresh();
    if (!refresh) {
      return false;
    }
    const response = await send('/auth/token/refresh/', {
      method: 'POST',
      body: { refresh },
      auth: false,
    });
    if (!response.ok) {
      return false;
    }
    const data = await readBody(response);
    Auth.setAccess(data.access);
    return true;
  }

  // Beberapa permintaan yang gagal bersamaan berbagi satu penukaran.
  let exchanging = null;
  function renewAccessToken() {
    if (!exchanging) {
      exchanging = exchangeRefreshToken().finally(() => {
        exchanging = null;
      });
    }
    return exchanging;
  }

  // Hasilnya selalu { ok, status, data }. Isi `data` adalah JSON dari server.
  async function request(path, options = {}) {
    let response;
    try {
      response = await send(path, options);
      if (response.status === 401 && options.auth !== false) {
        const renewed = await renewAccessToken();
        if (renewed) {
          response = await send(path, options);
        }
        if (!renewed || response.status === 401) {
          Auth.clear();
          Auth.redirectToLogin();
        }
      }
    } catch {
      return {
        ok: false,
        status: 0,
        data: { detail: 'Tidak bisa terhubung ke server.' },
      };
    }
    return {
      ok: response.ok,
      status: response.status,
      data: await readBody(response),
    };
  }

  return { request };
})();