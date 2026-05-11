console.log("PhishGuard Elite content script loaded");

let lastUrl = location.href;
const processedRows = new Set();

// ----------------------------------------------------------------------------
// PERSIST RESULT TO chrome.storage.local
// ----------------------------------------------------------------------------
function persistScanResult(sender, data) {
    chrome.storage.local.get(['pg_scanned', 'pg_blocked', 'pg_threats'], (stored) => {
        const scanned = (stored.pg_scanned || 0) + 1;
        const severity = (data.severity || '').toLowerCase().replace(' ', '');
        const isThreat = severity !== 'safe';
        const blocked = (stored.pg_blocked || 0) + (isThreat ? 1 : 0);

        // Keep last 50 threats only
        const threats = stored.pg_threats || [];
        if (isThreat) {
            threats.unshift({
                sender: sender,
                severity: data.severity,
                confidence: data.confidence,
                reasons: data.reasons || [],
                impersonated_brand: data.impersonated_brand || null,
                timestamp: Date.now()
            });
            if (threats.length > 50) threats.length = 50;
        }

        chrome.storage.local.set({
            pg_scanned: scanned,
            pg_blocked: blocked,
            pg_threats: threats
        });
    });
}

// ----------------------------------------------------------------------------
// THREAT DETAIL MODAL (Overlay)
// ----------------------------------------------------------------------------
function showThreatModal(data) {
    const existingModal = document.getElementById("phishguard-modal");
    if (existingModal) existingModal.remove();

    const overlay = document.createElement("div");
    overlay.id = "phishguard-modal";
    overlay.style.position = "fixed";
    overlay.style.top = "0";
    overlay.style.left = "0";
    overlay.style.width = "100vw";
    overlay.style.height = "100vh";
    overlay.style.backgroundColor = "rgba(11, 16, 32, 0.8)";
    overlay.style.backdropFilter = "blur(10px)";
    overlay.style.zIndex = "10000";
    overlay.style.display = "flex";
    overlay.style.alignItems = "center";
    overlay.style.justifyContent = "center";

    const modal = document.createElement("div");
    modal.className = "glass-panel flex-col gap-4 fade-in";
    modal.style.width = "600px";
    modal.style.padding = "32px";
    modal.style.color = "var(--text-primary)";
    modal.style.fontFamily = "'Inter', sans-serif";

    let reasonsHtml = data.reasons.map(r => `<li>${r}</li>`).join("");

    modal.innerHTML = `
        <div class="flex-row justify-between items-center" style="border-bottom: 1px solid var(--glass-border); padding-bottom: 16px;">
            <h1 class="text-h1" style="color: var(--accent-cyan);">Threat Intelligence Report</h1>
            <button id="pg-close-btn" style="background:none; border:none; color:white; font-size: 24px; cursor:pointer;">&times;</button>
        </div>
        
        <div class="flex-row justify-between items-center" style="margin-top:16px;">
            <span class="text-h2">Verdict: <span class="color-${data.severity.toLowerCase().replace(' ', '')}">${data.severity}</span></span>
            <span class="badge badge-${data.severity.toLowerCase().replace(' ', '')}">Confidence: ${(data.confidence * 100).toFixed(1)}%</span>
        </div>

        <div style="background: var(--glass-bg); padding: 16px; border-radius: 8px;">
            <h2 class="text-body" style="font-weight: 700; margin-bottom: 8px;">AI Reasoning Timeline</h2>
            <ul style="margin: 0; padding-left: 20px; font-size: 14px; color: var(--text-secondary);">
                ${reasonsHtml || "<li>No suspicious indicators found.</li>"}
            </ul>
        </div>

        <div class="flex-row justify-between" style="margin-top: 8px;">
            <div class="flex-col gap-2" style="background: var(--glass-bg); padding: 16px; border-radius: 8px; width: 48%;">
                <span class="text-caption">Sender Trust Score</span>
                <span class="text-h2">${data.sender_trust_score.toFixed(1)} / 100</span>
            </div>
            <div class="flex-col gap-2" style="background: var(--glass-bg); padding: 16px; border-radius: 8px; width: 48%;">
                <span class="text-caption">Suspicious Links</span>
                <span class="text-h2">${data.suspicious_links_count}</span>
            </div>
        </div>
    `;

    overlay.appendChild(modal);
    document.body.appendChild(overlay);

    document.getElementById('pg-close-btn').addEventListener('click', () => {
        overlay.remove();
    });
}

// ----------------------------------------------------------------------------
// GMAIL WARNING BANNER
// ----------------------------------------------------------------------------
function showWarningBanner(data) {
    const existingBanner = document.getElementById("phishguard-banner");
    if (existingBanner) existingBanner.remove();

    const banner = document.createElement("div");
    banner.id = "phishguard-banner";
    
    // Use global CSS styles injected via manifest
    const severityClass = data.severity.toLowerCase().replace(' ', '');
    banner.className = `glass-card bg-${severityClass} fade-in flex-row justify-between items-center`;
    
    banner.style.padding = "16px 24px";
    banner.style.margin = "16px 0";
    banner.style.color = "var(--text-primary)";
    banner.style.fontFamily = "'Inter', sans-serif";
    
    if (severityClass === 'critical') banner.classList.add('pulse-red');
    if (severityClass === 'safe') banner.classList.add('pulse-green');

    let icon = "✅";
    if (severityClass === "suspicious") icon = "⚠️";
    if (severityClass === "highrisk") icon = "🛑";
    if (severityClass === "critical") icon = "☠️";

    let reasonsSummary = data.reasons.slice(0, 2).join(' • ');
    if (data.reasons.length > 2) reasonsSummary += ` (+${data.reasons.length - 2} more)`;

    banner.innerHTML = `
        <div class="flex-col gap-2">
            <span style="font-size: 18px; font-weight: 700;">
                ${icon} <span class="color-${severityClass}">${data.prediction} PHISHING DETECTED</span>
            </span>
            <span class="text-body">${reasonsSummary}</span>
        </div>
        <button id="pg-details-btn" style="background: rgba(255,255,255,0.1); border: 1px solid var(--glass-border); color: white; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-weight: 600;">View Details</button>
    `;

    const subjectLine = document.querySelector('h2.hP');
    if (subjectLine && subjectLine.parentElement) {
        subjectLine.parentElement.insertBefore(banner, subjectLine);
    }

    // Attach modal listener
    setTimeout(() => {
        const btn = document.getElementById('pg-details-btn');
        if (btn) {
            btn.addEventListener('click', () => showThreatModal(data));
        }
    }, 100);
}

// ----------------------------------------------------------------------------
// INBOX SCANNING (List View)
// ----------------------------------------------------------------------------
async function scanInboxRow(row) {
    if (processedRows.has(row) || row.getAttribute('data-phishguard-scanned')) return;
    row.setAttribute('data-phishguard-scanned', 'true');
    processedRows.add(row);

    const senderEl = row.querySelector('.yP,.zF');
    const subjectEl = row.querySelector('.bog');
    
    if (!senderEl || !subjectEl) return;

    const sender = senderEl.getAttribute('email') || senderEl.innerText;
    const subject = subjectEl.innerText;

    // We don't have the body text yet in list view, so we analyze sender + subject
    const payload = {
        sender: sender,
        subject: subject,
        body_text: "",
        body_html: "",
        links: []
    };

    try {
        const response = await fetch("http://127.0.0.1:8000/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        
        // Inject Icon next to subject
        const severityClass = data.severity.toLowerCase().replace(' ', '');
        let iconHtml = `<span style="margin-right: 8px;" class="color-${severityClass}">`;
        
        if (severityClass === "safe") iconHtml += "✅";
        else if (severityClass === "suspicious") iconHtml += "⚠️";
        else if (severityClass === "highrisk") iconHtml += "🛑";
        else iconHtml += "☠️";
        
        iconHtml += "</span>";

        const iconContainer = document.createElement("span");
        iconContainer.innerHTML = iconHtml;
        subjectEl.parentElement.insertBefore(iconContainer, subjectEl);

        if (severityClass === "critical") {
            row.style.backgroundColor = "rgba(255, 23, 68, 0.05)";
        }

        // Persist real result
        persistScanResult(sender, data);

    } catch (e) {
        // Backend offline or error
    }
}

// ----------------------------------------------------------------------------
// FULL EMAIL EXTRACTION
// ----------------------------------------------------------------------------
async function sendToBackend(payload) {
    try {
        const response = await fetch("http://127.0.0.1:8000/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        showWarningBanner(data);
        // Persist real result
        persistScanResult(payload.sender, data);
    } catch (error) {
        console.error("❌ Backend error:", error);
    }
}

function extractEmailData() {
    const subjectElement = document.querySelector('h2.hP');
    const bodyElement = document.querySelector('div.a3s.aiL');
    const senderElement = document.querySelector('span.gD') || document.querySelector('span.go');

    if (subjectElement && bodyElement) {
        const payload = {
            sender: senderElement ? (senderElement.getAttribute('email') || senderElement.innerText.replace(/[<>]/g, '').trim()) : "",
            subject: subjectElement.innerText.trim(),
            body_text: bodyElement.innerText.trim(),
            body_html: bodyElement.innerHTML,
            links: Array.from(bodyElement.querySelectorAll('a')).map(a => a.href)
        };
        sendToBackend(payload);
    }
}

// ----------------------------------------------------------------------------
// OBSERVER
// ----------------------------------------------------------------------------
const observer = new MutationObserver(() => {
    // 1. Check for email view
    if (location.href !== lastUrl) {
        lastUrl = location.href;
        const isEmailView = location.hash.match(/#(inbox|spam|all|trash|sent|important|starred)\//) && location.hash.length > 10;
        if (isEmailView) {
            setTimeout(extractEmailData, 2500);
        }
    }

    // 2. Continually check for inbox rows to scan
    const isListView = location.hash === "#inbox" || location.hash === "";
    if (isListView) {
        const rows = document.querySelectorAll('tr.zA');
        rows.forEach(row => scanInboxRow(row));
    }
});

observer.observe(document.body, { childList: true, subtree: true });
