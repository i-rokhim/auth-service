// auth.js: penyimpanan token dan pengalihan halaman.
// Dimuat sebelum api.js, karena api.js memakai objek Auth.

const Auth = (() => {
  const ACCESS_KEY = 'auth.access';
  const REFRESH_KEY = 'auth.refresh';
  const USER_KEY = 'auth.user';

  const LOGIN_PAGE = 'index.html';
  const HOME_PAGE = 'profile.html';

  function saveSession({ access, refresh, user }) {
    localStorage.setItem(ACCESS_KEY, access);
    localStorage.setItem(REFRESH_KEY, refresh);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  // Endpoint refresh hanya mengembalikan access token baru.
  function setAccess(access) {
    localStorage.setItem(ACCESS_KEY, access);
  }

  function getAccess() {
    return localStorage.getItem(ACCESS_KEY);
  }

  function getRefresh() {
    return localStorage.getItem(REFRESH_KEY);
  }

  function getUser() {
    try {
      return JSON.parse(localStorage.getItem(USER_KEY));
    } catch {
      return null;
    }
  }

  function isLoggedIn() {
    return Boolean(getRefresh());
  }

  function clear() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
  }

  function currentPage() {
    return window.location.pathname.split('/').pop() || LOGIN_PAGE;
  }

  function redirectToLogin() {
    if (currentPage() !== LOGIN_PAGE) {
      window.location.replace(LOGIN_PAGE);
    }
  }

  function redirectToHome() {
    if (currentPage() !== HOME_PAGE) {
      window.location.replace(HOME_PAGE);
    }
  }

  // Halaman yang butuh login memanggil ini di awal.
  function requireLogin() {
    if (!isLoggedIn()) {
      redirectToLogin();
      return false;
    }
    return true;
  }

  // Halaman login dan daftar memanggil ini: yang sudah login langsung ke profil.
  function redirectIfLoggedIn() {
    if (isLoggedIn()) {
      redirectToHome();
      return true;
    }
    return false;
  }

  return {
    saveSession,
    setAccess,
    getAccess,
    getRefresh,
    getUser,
    isLoggedIn,
    clear,
    redirectToLogin,
    redirectToHome,
    requireLogin,
    redirectIfLoggedIn,
  };
})();