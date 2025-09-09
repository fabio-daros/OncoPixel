window.startHeartbeatMonitor = function startHeartbeatMonitor() {
  const el = document.getElementById('oncobrain-status');
  if (!el) return;

  const url = el.dataset.heartbeatUrl || '/image-analysis/oncobrain-heartbeat/';

  let setStatus = (s) => el.setAttribute('data-status', s);
  try {
    if (window.Alpine && Alpine.$data) {
      const data = Alpine.$data(el);
      if (data && typeof data === 'object') setStatus = (s) => { data.status = s; };
    }
  } catch (_) {}

  async function ping() {
    setStatus('checking');
    try {
      const r = await fetch(url, { headers: { 'Accept': 'application/json' } });
      if (!r.ok) throw new Error(r.status);
      const j = await r.json();
      setStatus(j && j.status === 'online' ? 'online' : 'offline');
    } catch {
      setStatus('offline');
    }
  }

  ping();
  setInterval(ping, 20000);
};
