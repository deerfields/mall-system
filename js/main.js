// SPA Router, Session, Login Example
import { initRouter } from './utils.js';
import { login } from './auth.js';

window.addEventListener('DOMContentLoaded', () => {
  initRouter();
  // اگر کاربر لاگین نیست، فرم لاگین نمایش داده شود
  if (!sessionStorage.getItem('token')) {
    login();
  }
}); 