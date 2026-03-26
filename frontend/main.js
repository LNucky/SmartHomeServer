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
// Симуляция датчиков (для главной и комнат)
function updateSensorsMain() {
    const t1 = (22 + Math.random() * 3).toFixed(1);
    const t2 = (20 + Math.random() * 3).toFixed(1);
    const h1 = Math.round(55 + Math.random() * 10);
    const h2 = Math.round(52 + Math.random() * 10);
    const l = Math.round(650 + Math.random() * 300);
    const avgT = ((parseFloat(t1) + parseFloat(t2)) / 2).toFixed(1);
    const avgH = Math.round((h1 + h2) / 2);
    const avgTempEl = document.getElementById('avg-temp');
    const avgHumEl = document.getElementById('avg-hum');
    const avgLightEl = document.getElementById('avg-light');
    if (avgTempEl) avgTempEl.textContent = avgT;
    if (avgHumEl) avgHumEl.textContent = avgH;
    if (avgLightEl) avgLightEl.textContent = l;
    const tempBar = document.getElementById('avg-temp-bar');
    if (tempBar) tempBar.style.width = Math.min(100, (avgT / 40 * 100)) + '%';
    const humBar = document.getElementById('avg-hum-bar');
    if (humBar) humBar.style.width = avgH + '%';
    const r1temp = document.getElementById('r1-temp');
    const r1hum = document.getElementById('r1-hum');
    const r2temp = document.getElementById('r2-temp');
    const r2hum = document.getElementById('r2-hum');
    if (r1temp) r1temp.textContent = t1;
    if (r1hum) r1hum.textContent = h1;
    if (r2temp) r2temp.textContent = t2;
    if (r2hum) r2hum.textContent = h2;
}

// Для комнат
function updateRoomSensors(room) {
    if (room === 1) {
        const t = (22 + Math.random() * 3).toFixed(1);
        const h = Math.round(54 + Math.random() * 10);
        const tempEl = document.getElementById('r1-temp');
        const humEl = document.getElementById('r1-hum');
        if (tempEl) tempEl.textContent = t;
        if (humEl) humEl.textContent = h;
        const tempBar = document.getElementById('r1-temp-bar');
        if (tempBar) tempBar.style.width = Math.min(100, (t / 40 * 100)) + '%';
        const humBar = document.getElementById('r1-hum-bar');
        if (humBar) humBar.style.width = h + '%';
    } else if (room === 2) {
        const t = (20 + Math.random() * 3).toFixed(1);
        const h = Math.round(50 + Math.random() * 10);
        const tempEl = document.getElementById('r2-temp');
        const humEl = document.getElementById('r2-hum');
        if (tempEl) tempEl.textContent = t;
        if (humEl) humEl.textContent = h;
        const tempBar = document.getElementById('r2-temp-bar');
        if (tempBar) tempBar.style.width = Math.min(100, (t / 40 * 100)) + '%';
        const humBar = document.getElementById('r2-hum-bar');
        if (humBar) humBar.style.width = h + '%';
    }
}

// Запуск симуляции датчиков в зависимости от страницы
function startSensorsSimulation() {
    const isMain = !!document.getElementById('avg-temp');
    const isRoom1 = !!document.getElementById('r1-temp') && !document.getElementById('avg-temp');
    const isRoom2 = !!document.getElementById('r2-temp') && !document.getElementById('avg-temp');
    if (isMain) {
        setInterval(updateSensorsMain, 5000);
        updateSensorsMain();
    } else if (isRoom1) {
        setInterval(() => updateRoomSensors(1), 5000);
        updateRoomSensors(1);
    } else if (isRoom2) {
        setInterval(() => updateRoomSensors(2), 5000);
        updateRoomSensors(2);
    }
}

// ─────────────────────────────────────────────────────────────────────────
// Вентиляция (главная страница)
let ventAutoMain = false;
let ventTempMain = 22;
function togVentMain() {
    const b = document.getElementById('vent-tog');
    if (!b) return;
    b.classList.toggle('on');
    const on = b.classList.contains('on');
    const stateLbl = document.getElementById('vent-state-lbl');
    if (stateLbl) stateLbl.textContent = on ? 'Включена' : 'Выключена';
    notify(on ? '🌀 Вентиляция включена' : '🌀 Вентиляция выключена');
}
function adjTempMain(d) {
    ventTempMain = Math.min(30, Math.max(16, ventTempMain + d));
    const tEl = document.getElementById('vent-temp');
    if (tEl) tEl.textContent = ventTempMain;
}
function togVentAutoMain() {
    ventAutoMain = !ventAutoMain;
    const autoTog = document.getElementById('vent-auto-tog');
    if (autoTog) autoTog.classList.toggle('on', ventAutoMain);
    const autoLbl = document.getElementById('vent-auto-lbl');
    if (autoLbl) autoLbl.textContent = ventAutoMain ? 'Включён — авто по темп./влажн.' : 'Выключен';
    const controls = document.getElementById('vent-controls');
    if (controls) controls.classList.toggle('locked', ventAutoMain);
    const badge = document.getElementById('vent-auto-badge');
    if (badge) badge.classList.toggle('show', ventAutoMain);
    notify(ventAutoMain ? '🌀 Авто: управление заблокировано' : '🌀 Авто выключен');
}

// Экспорт в глобальную область для использования в HTML-обработчиках
window.togVentMain = togVentMain;
window.adjTempMain = adjTempMain;
window.togVentAutoMain = togVentAutoMain;

// ─────────────────────────────────────────────────────────────────────────
// Инициализация страницы
document.addEventListener('DOMContentLoaded', () => {
    initAuth();
    initMobileMenu();
    initProfileDropdown();
    startSensorsSimulation();
    // Для главной страницы инициализация вентиляции (если есть элементы)
    if (document.getElementById('vent-tog')) {
        // кнопки уже привязаны через onclick, просто инициализируем переменные
        ventTempMain = 22;
        const tEl = document.getElementById('vent-temp');
        if (tEl) tEl.textContent = ventTempMain;
    }
});