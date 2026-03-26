// main.js – общие функции: авторизация, часы, уведомления, меню, профиль, датчики, вентиляция

// ─────────────────────────────────────────────────────────────────────────
// Авторизация
function getSession() {
    try {
        return JSON.parse(localStorage.getItem('sh_user'));
    } catch (e) {
        return null;
    }
}

function requireAuth() {
    const user = getSession();
    if (!user) {
        location.href = 'authorization.html';
        return false;
    }
    return user;
}

// Инициализация аватара и профиля
function initAuth() {
    const user = requireAuth();
    if (!user) return;
    const ava = document.getElementById('ava');
    if (ava) ava.textContent = user.name[0].toUpperCase();
    const ddName = document.getElementById('dd-name');
    const ddLogin = document.getElementById('dd-login');
    if (ddName) ddName.textContent = user.name;
    if (ddLogin) ddLogin.textContent = '@' + user.username;
    const heroName = document.getElementById('hero-name');
    if (heroName) heroName.textContent = user.name;
}

// ─────────────────────────────────────────────────────────────────────────
// Часы и дата
function updateClock() {
    const now = new Date();
    const clockEl = document.getElementById('clock');
    if (clockEl) clockEl.textContent = now.toTimeString().split(' ')[0].slice(0, 5);
    const days = ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'];
    const months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
    const dateStr = days[now.getDay()] + ', ' + now.getDate() + ' ' + months[now.getMonth()] + ' ' + now.getFullYear();
    const heroDate = document.getElementById('hero-date');
    if (heroDate) heroDate.textContent = dateStr;
    const r1clock = document.getElementById('r1-clock');
    if (r1clock) r1clock.textContent = now.toTimeString().split(' ')[0].slice(0, 5);
    const r2clock = document.getElementById('r2-clock');
    if (r2clock) r2clock.textContent = now.toTimeString().split(' ')[0].slice(0, 5);
    const camTime = document.getElementById('cam-time');
    if (camTime) camTime.textContent = now.toTimeString().split(' ')[0];
}
setInterval(updateClock, 1000);
updateClock();

// ─────────────────────────────────────────────────────────────────────────
// Уведомления
function notify(msg) {
    const old = document.querySelector('.notif');
    if (old) old.remove();
    const n = document.createElement('div');
    n.className = 'notif';
    n.textContent = msg;
    document.body.appendChild(n);
    setTimeout(() => {
        n.style.animation = 'nout 0.3s ease';
        setTimeout(() => n.remove(), 280);
    }, 2500);
}
window.notify = notify;

// ─────────────────────────────────────────────────────────────────────────
// Мобильное меню
function initMobileMenu() {
    const btn = document.getElementById('burger-btn');
    const menu = document.getElementById('mobile-nav');
    if (!btn || !menu) return;
    btn.addEventListener('click', (e) => {
        e.stopPropagation();
        btn.classList.toggle('open');
        menu.classList.toggle('open');
    });
    document.addEventListener('click', (e) => {
        if (!btn.contains(e.target) && !menu.contains(e.target)) {
            btn.classList.remove('open');
            menu.classList.remove('open');
        }
    });
    menu.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', () => {
            btn.classList.remove('open');
            menu.classList.remove('open');
        });
    });
}

// ─────────────────────────────────────────────────────────────────────────
// Профиль дропдаун
function initProfileDropdown() {
    const ava = document.getElementById('ava');
    const dd = document.getElementById('profile-dropdown');
    if (!ava || !dd) return;
    ava.addEventListener('click', (e) => {
        e.stopPropagation();
        dd.classList.toggle('visible');
    });
    document.addEventListener('click', (e) => {
        if (!dd.contains(e.target)) dd.classList.remove('visible');
    });
    const logout = document.getElementById('dd-logout');
    if (logout) {
        logout.addEventListener('click', () => {
            localStorage.removeItem('sh_user');
            location.href = 'authorization.html';
        });
    }
}

// ─────────────────────────────────────────────────────────────────────────
// Вентиляция (главная страница)
let ventAutoMain = false;
function togVentMain() {
    const b = document.getElementById('vent-tog');
    if (!b) return;
    b.classList.toggle('on');
    const on = b.classList.contains('on');
    const stateLbl = document.getElementById('vent-state-lbl');
    if (stateLbl) stateLbl.textContent = on ? 'Включена' : 'Выключена';
    notify(on ? '🌀 Вентиляция включена' : '🌀 Вентиляция выключена');
}
function togVentAutoMain() {
    ventAutoMain = !ventAutoMain;
    const autoTog = document.getElementById('vent-auto-tog');
    if (autoTog) autoTog.classList.toggle('on', ventAutoMain);
    const autoLbl = document.getElementById('vent-auto-lbl');
    if (autoLbl) autoLbl.textContent = ventAutoMain ? 'Включён — авто по темп./влажн.' : 'Выключен';
    const badge = document.getElementById('vent-auto-badge');
    if (badge) badge.classList.toggle('show', ventAutoMain);
    notify(ventAutoMain ? '🌀 Авто: управление заблокировано' : '🌀 Авто выключен');
}

// Экспорт в глобальную область для использования в HTML-обработчиках
window.togVentMain = togVentMain;
window.togVentAutoMain = togVentAutoMain;

// ─────────────────────────────────────────────────────────────────────────
// Инициализация страницы
document.addEventListener('DOMContentLoaded', () => {
    initAuth();
    initMobileMenu();
    initProfileDropdown();
});