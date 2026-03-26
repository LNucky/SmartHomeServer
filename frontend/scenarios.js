// Сценарии и авто — только с сервера (/api/scenario, /api/devices)

const API = '';

let currentScenario = 'sleep';
let autoMode = true;
/** При выключенном авто не перезаписываем ползунки/тогглы из API после первой гидратации. */
let manualDeviceHydrated = false;

function resetManualDeviceHydration() {
    manualDeviceHydrated = false;
}

function apiFetch(path, options = {}) {
    const o = { ...options, headers: { 'Content-Type': 'application/json', ...options.headers } };
    return fetch(API + path, o);
}

async function loadScenarioFromServer() {
    const r = await apiFetch('/api/scenario');
    if (!r.ok) return;
    const d = await r.json();
    currentScenario = d.scenario;
    autoMode = d.auto_mode;
    window.smartHomeAuto = autoMode;
    window.smartHomeScenario = currentScenario;
    if (!autoMode) resetManualDeviceHydration();
    updateUIByScenario();
}

async function saveScenario(scenario, explicitAutoMode) {
    const body = { scenario };
    if (explicitAutoMode !== undefined) body.auto_mode = explicitAutoMode;
    else if (scenario !== 'sleep') body.auto_mode = true;
    const r = await apiFetch('/api/scenario', { method: 'PUT', body: JSON.stringify(body) });
    if (!r.ok) throw new Error('scenario ' + r.status);
    const d = await r.json();
    currentScenario = d.scenario;
    autoMode = d.auto_mode;
    window.smartHomeAuto = autoMode;
    window.smartHomeScenario = currentScenario;
    if (!autoMode) resetManualDeviceHydration();
    updateUIByScenario();
    await refreshDevicesFromServer();
}

window.toggleAuto = async function () {
    const r = await apiFetch('/api/scenario', {
        method: 'PUT',
        body: JSON.stringify({ auto_mode: !autoMode }),
    });
    if (!r.ok) return;
    const d = await r.json();
    autoMode = d.auto_mode;
    window.smartHomeAuto = autoMode;
    window.smartHomeScenario = currentScenario;
    if (!autoMode) resetManualDeviceHydration();
    updateUIByScenario();
    await refreshDevicesFromServer();
};

function updateUIByScenario() {
    const autoToggle = document.getElementById('global-auto-toggle');
    if (autoToggle) {
        if (autoMode) autoToggle.classList.add('on');
        else autoToggle.classList.remove('on');
    }

    const isSleep = currentScenario === 'sleep';
    const lock = isSleep || autoMode;

    document.querySelectorAll('.lockable').forEach((el) => {
        if (lock) el.classList.add('locked');
        else el.classList.remove('locked');
    });

    const overlay = document.getElementById('sleep-overlay');
    if (overlay) overlay.style.display = isSleep ? 'flex' : 'none';

    const autoBlock = document.getElementById('auto-control');
    if (autoBlock) autoBlock.style.display = isSleep ? 'none' : 'flex';

    const noScenarioMsg = document.getElementById('no-scenario-message');
    if (noScenarioMsg) noScenarioMsg.style.display = isSleep ? 'block' : 'none';
}

function hidePerDeviceAutoRows() {
    ['light-auto-tog', 'vent-auto-tog', 'light-auto-tog2', 'vent-auto-tog2', 'blind-auto-tog'].forEach((id) => {
        const t = document.getElementById(id);
        const row = t && t.closest('.row.gi');
        if (row) row.style.display = 'none';
    });
    ['light-auto-badge', 'vent-auto-badge', 'light-auto-badge2', 'vent-auto-badge2', 'blind-auto-badge'].forEach((id) => {
        const b = document.getElementById(id);
        if (b) b.style.display = 'none';
    });
}

function devOn(list, type, room) {
    const x = list.find((d) => d.device_type === type && d.room_id === room);
    return x ? x.is_on : false;
}

function setToggle(id, on) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.toggle('on', !!on);
}

function setSock(onTv, onAc) {
    setToggle('sock-tog-tv', onTv);
    setToggle('sock-tog-ac', onAc);
}

function applyServoToBlinds(isUp) {
    const tog = document.getElementById('blind-tog');
    const cover = document.getElementById('blind-cover');
    const st = document.getElementById('blind-state');
    if (tog) tog.classList.toggle('on', isUp);
    if (cover) cover.style.opacity = isUp ? '0' : '0.85';
    if (st) st.textContent = isUp ? 'Открыты' : 'Закрыты';
}

async function refreshDevicesFromServer() {
    const r = await apiFetch('/api/devices');
    if (!r.ok) return;
    const devices = await r.json();
    window.__lastDevices = devices;

    if (!autoMode && manualDeviceHydrated) return;

    const path = location.pathname || '';
    if (path.includes('room1')) {
        const v1 = devOn(devices, 'vent', 1);
        const d1 = devOn(devices, 'day_light', 1);
        const n1 = devOn(devices, 'night_light', 1);
        setToggle('vent-tog', v1);
        const vs = document.getElementById('vent-state');
        if (vs) vs.textContent = v1 ? 'Включена' : 'Выключена';
        const anyLight = d1 || n1;
        setToggle('light-tog', anyLight);
        const ls = document.getElementById('light-state');
        if (ls) ls.textContent = anyLight ? 'Включено' : 'Выключено';
        if (typeof window.setLightMode === 'function') {
            if (d1 && !n1) window.setLightMode('day', true);
            else if (n1 && !d1) window.setLightMode('night', true);
            else if (d1 && n1) window.setLightMode('day', true);
        }
        if (typeof window.syncRoom1Light === 'function') window.syncRoom1Light(anyLight);
        setSock(devOn(devices, 'socket_tv', 1), devOn(devices, 'socket_ac', 1));
    }
    if (path.includes('room2')) {
        const v2 = devOn(devices, 'vent', 2);
        const d2 = devOn(devices, 'day_light', 2);
        const n2 = devOn(devices, 'night_light', 2);
        setToggle('vent-tog2', v2);
        const vs2 = document.getElementById('vent-state2');
        if (vs2) vs2.textContent = v2 ? 'Включена' : 'Выключена';
        const anyL2 = d2 || n2;
        setToggle('light-tog2', anyL2);
        const ls2 = document.getElementById('light-state2');
        if (ls2) ls2.textContent = anyL2 ? 'Включено' : 'Выключено';
        if (typeof window.setLightMode === 'function') {
            if (d2 && !n2) window.setLightMode('day', true);
            else if (n2 && !d2) window.setLightMode('night', true);
            else if (d2 && n2) window.setLightMode('day', true);
        }
        if (typeof window.syncRoom2Light === 'function') window.syncRoom2Light(anyL2);
        setSock(devOn(devices, 'socket_tv', 2), devOn(devices, 'socket_ac', 2));
        const servoUp = devOn(devices, 'servo', 2);
        applyServoToBlinds(servoUp);
        if (typeof window.syncBlindFromServer === 'function') window.syncBlindFromServer(servoUp);
    }
    const strip = document.getElementById('light-strip-toggle');
    if (strip) strip.classList.toggle('on', devOn(devices, 'rgb', 1));

    if (!autoMode) manualDeviceHydrated = true;
}

function sensorVal(list, name, room) {
    const it = list.find((x) => x.sensor_name === name && x.room_id === room);
    return it ? it.value : null;
}

function setSensorText(id, v, fix) {
    const el = document.getElementById(id);
    if (!el) return;
    if (v == null) {
        el.textContent = '—';
        return;
    }
    el.textContent = typeof fix === 'number' ? Number(v).toFixed(fix) : String(v);
}

function setBarWidth(id, pct) {
    const el = document.getElementById(id);
    if (el) el.style.width = Math.min(100, Math.max(0, pct)) + '%';
}

async function refreshSensorsFromServer() {
    const r = await apiFetch('/api/sensors/latest');
    if (!r.ok) return;
    const list = await r.json();
    const val = (name, room) => sensorVal(list, name, room);

    const t1 = val('temperature', 1);
    const t2 = val('temperature', 2);
    const h1 = val('humidity', 1);
    const h2 = val('humidity', 2);
    const lux = val('light_level', 1);

    if (document.getElementById('avg-temp')) {
        if (t1 != null && t2 != null) {
            const avgT = ((t1 + t2) / 2).toFixed(1);
            setSensorText('avg-temp', avgT);
            setBarWidth('avg-temp-bar', (parseFloat(avgT) / 40) * 100);
        } else {
            setSensorText('avg-temp', null);
        }
        if (h1 != null && h2 != null) {
            const avgH = Math.round((h1 + h2) / 2);
            setSensorText('avg-hum', avgH, 0);
            setBarWidth('avg-hum-bar', avgH);
        } else {
            setSensorText('avg-hum', null);
        }
        if (lux != null) {
            setSensorText('avg-light', Math.round(lux), 0);
            setBarWidth('avg-light-bar', Math.min(100, (lux / 1200) * 100));
        } else {
            setSensorText('avg-light', null);
        }
    }

    setSensorText('r1-temp', t1, 1);
    setSensorText('r1-hum', h1, 0);
    setSensorText('r2-temp', t2, 1);
    setSensorText('r2-hum', h2, 0);

    if (document.getElementById('r1-temp-bar') && t1 != null) {
        setBarWidth('r1-temp-bar', (t1 / 40) * 100);
    }
    if (document.getElementById('r1-hum-bar') && h1 != null) {
        setBarWidth('r1-hum-bar', h1);
    }
    if (document.getElementById('r2-temp-bar') && t2 != null) {
        setBarWidth('r2-temp-bar', (t2 / 40) * 100);
    }
    if (document.getElementById('r2-hum-bar') && h2 != null) {
        setBarWidth('r2-hum-bar', h2);
    }
}

async function initScenarios() {
    hidePerDeviceAutoRows();
    try {
        await loadScenarioFromServer();
        await refreshDevicesFromServer();
        await refreshSensorsFromServer();
    } catch (e) {
        console.warn('API недоступен', e);
    }
    setInterval(() => {
        refreshDevicesFromServer();
        refreshSensorsFromServer();
    }, 8000);
}

window.saveScenario = saveScenario;
window.initScenarios = initScenarios;
window.updateUIByScenario = updateUIByScenario;
window.refreshDevicesFromServer = refreshDevicesFromServer;
window.refreshSensorsFromServer = refreshSensorsFromServer;
