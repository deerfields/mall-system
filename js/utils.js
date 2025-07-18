import QRCode from 'qrcode';

export function generateQR(data, elementId) {
  // تولید QR کد و نمایش در یک المنت با id مشخص
  if (!elementId) return;
  QRCode.toCanvas(document.getElementById(elementId), data, function (error) {
    if (error) console.error(error);
  });
}

export function formatDate(date, locale = 'fa-IR') {
  // فرمت تاریخ شمسی/میلادی
  if (!date) return '';
  const d = new Date(date);
  return d.toLocaleDateString(locale);
}

export function encrypt(text) {
  // رمزنگاری ساده با Base64
  return btoa(unescape(encodeURIComponent(text)));
}

export function initRouter() {
  // راه‌اندازی روتر SPA ساده با hashchange
  window.addEventListener('hashchange', () => {
    const page = location.hash.replace('#', '');
    document.querySelectorAll('[data-route]').forEach(el => {
      el.style.display = el.getAttribute('data-route') === page ? 'block' : 'none';
    });
  });
  // نمایش صفحه فعلی در بارگذاری اولیه
  window.dispatchEvent(new Event('hashchange'));
} 