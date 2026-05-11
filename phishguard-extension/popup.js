document.addEventListener('DOMContentLoaded', async () => {
  const backendDot = document.getElementById('backend-dot');
  const backendStatus = document.getElementById('backend-status');
  const modelStatus = document.getElementById('model-status');
  const scannedCount = document.getElementById('scanned-count');
  const blockedCount = document.getElementById('blocked-count');
  const threatList = document.getElementById('threat-list');

  // ── 1. Check backend health (4s timeout) ────────────────────────────────
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 4000);
    const response = await fetch("http://127.0.0.1:8000/", { signal: controller.signal });
    clearTimeout(timeoutId);
    if (response.ok) {
      backendDot.className = "status-dot pulse-green";
      backendStatus.innerText = "FastAPI Connected";
      modelStatus.innerText = "BERT Online";
      modelStatus.className = "badge badge-safe";
    } else {
      throw new Error("non-200");
    }
  } catch {
    backendDot.className = "status-dot error";
    backendStatus.innerText = "Backend Offline";
    modelStatus.innerText = "Unavailable";
    modelStatus.className = "badge badge-critical";
  }

  // ── 2. Load REAL stats from chrome.storage.local ─────────────────────────
  chrome.storage.local.get(['pg_scanned', 'pg_blocked', 'pg_threats'], (stored) => {
    const scanned = stored.pg_scanned || 0;
    const blocked = stored.pg_blocked || 0;
    const threats = stored.pg_threats || [];

    scannedCount.innerText = scanned;
    blockedCount.innerText = blocked;

    // ── 3. Render real threat list ─────────────────────────────────────────
    if (threats.length === 0) {
      threatList.innerHTML = `
        <div style="text-align:center; padding: 24px 0; color: var(--text-secondary); font-size: 13px;">
          <div style="font-size: 32px; margin-bottom: 8px;">✅</div>
          <div>No threats detected yet.</div>
          <div style="margin-top: 4px; font-size: 11px;">Open Gmail to start scanning emails.</div>
        </div>
      `;
      return;
    }

    threatList.innerHTML = threats.map(t => {
      const severityRaw = (t.severity || 'suspicious').toLowerCase().replace(' ', '');
      const badgeClass = {
        critical: 'badge-critical',
        highrisk: 'badge-highrisk',
        suspicious: 'badge-suspicious',
        safe: 'badge-safe'
      }[severityRaw] || 'badge-suspicious';

      const label = (t.severity || 'SUSPICIOUS').toUpperCase();
      const confidence = ((t.confidence || 0) * 100).toFixed(1);
      const reason = t.impersonated_brand
        ? `Impersonating brand: ${t.impersonated_brand}`
        : (t.reasons && t.reasons[0]) || 'Suspicious indicators detected';
      const sender = t.sender || 'Unknown Sender';
      const time = t.timestamp ? new Date(t.timestamp).toLocaleTimeString() : '';

      return `
        <div class="threat-item flex-col gap-2">
          <div class="flex-row justify-between items-center">
            <span class="text-caption" style="max-width:200px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${sender.toUpperCase()}</span>
            <span class="badge ${badgeClass}">${label}</span>
          </div>
          <span class="text-body" style="font-size: 12px;">${reason}</span>
          <span class="text-caption">CONFIDENCE: ${confidence}%${time ? ' · ' + time : ''}</span>
        </div>
      `;
    }).join('');
  });
});
