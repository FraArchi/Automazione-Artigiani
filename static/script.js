document.addEventListener('DOMContentLoaded', () => {
    refreshDashboard();
});

async function refreshDashboard() {
    await Promise.all([loadSummary(), loadLeads()]);
}

async function loadSummary() {
    const response = await fetch('/api/dashboard/summary');
    const data = await response.json();

    document.getElementById('count-new').textContent = data.counts.new || 0;
    document.getElementById('count-incomplete').textContent = data.counts.incomplete || 0;
    document.getElementById('count-needs-review').textContent = data.counts.needs_review || 0;
    document.getElementById('count-ready').textContent = data.counts.ready_for_quote || 0;
    document.getElementById('count-drafts').textContent = data.counts.draft_quotes || 0;
    document.getElementById('count-sent').textContent = data.counts.sent || 0;
    document.getElementById('count-error').textContent = data.counts.error || 0;

    document.getElementById('badge-incomplete').textContent = data.counts.incomplete || 0;
    document.getElementById('badge-needs-review').textContent = data.counts.needs_review || 0;
    document.getElementById('badge-draft').textContent = data.counts.draft_quotes || 0;
    document.getElementById('badge-sent').textContent = data.counts.sent || 0;

    const systemStatus = data.email_enabled
        ? 'Email abilitate: puoi inviare i preventivi dalla dashboard.'
        : 'Email disabilitate: ambiente sicuro/test, nessun invio reale.';

    document.getElementById('system-status').textContent = systemStatus;
    document.getElementById('receiver-current').textContent = `Destinatario attivo: ${data.active_receiver_email}`;
    document.getElementById('new-email').value = data.active_receiver_email || '';

    renderActivityLog(data.recent_activity || []);
}

async function loadLeads() {
    const response = await fetch('/api/leads');
    const data = await response.json();
    const leads = data.leads || [];

    const incomplete = leads.filter(lead => lead.status === 'incomplete');
    const needsReview = leads.filter(lead => lead.status === 'needs_review');
    const drafts = leads.filter(lead => lead.latest_quote && lead.latest_quote.status === 'draft');
    const sent = leads.filter(lead => lead.status === 'sent');

    renderLeadList('list-incomplete', incomplete, renderIncompleteLead);
    renderLeadList('list-needs-review', needsReview, renderNeedsReviewLead);
    renderLeadList('list-draft', drafts, renderDraftLead);
    renderLeadList('list-sent', sent, renderSentLead);
}

function renderLeadList(elementId, leads, renderer) {
    const container = document.getElementById(elementId);

    if (!leads.length) {
        container.className = 'lead-list empty-state';
        if (elementId === 'list-incomplete') container.textContent = 'Nessuna richiesta incompleta.';
        if (elementId === 'list-needs-review') container.textContent = 'Nessuna richiesta da verificare.';
        if (elementId === 'list-draft') container.textContent = 'Nessuna bozza pronta.';
        if (elementId === 'list-sent') container.textContent = 'Nessun preventivo inviato.';
        return;
    }

    container.className = 'lead-list';
    container.innerHTML = leads.map(renderer).join('');
}

function renderIncompleteLead(lead) {
    const missing = (lead.missing_fields || []).map(field => `<span class="pill warning">${escapeHtml(field)}</span>`).join('');
    return `
        <article class="lead-card">
            <div class="lead-top">
                <h3>${escapeHtml(lead.client_name || 'Cliente non indicato')}</h3>
                <span class="status status-warning">Incompleto</span>
            </div>
            <p class="lead-meta">Fonte: ${renderSourceLabel(lead.source)}</p>
            <p>${escapeHtml(lead.description || 'Nessuna descrizione')}</p>
            <div class="pill-row">${missing}</div>
            <p class="lead-note">${escapeHtml(lead.review_summary || '')}</p>
        </article>
    `;
}

function renderNeedsReviewLead(lead) {
    return `
        <article class="lead-card lead-card-attention">
            <div class="lead-top">
                <h3>${escapeHtml(lead.client_name || 'Cliente non indicato')}</h3>
                <span class="status status-danger">Needs review</span>
            </div>
            <p class="lead-meta">Fonte: ${renderSourceLabel(lead.source)}</p>
            <p>${escapeHtml(lead.description || 'Nessuna descrizione')}</p>
            <p class="lead-note">${escapeHtml(lead.review_summary || '')}</p>
        </article>
    `;
}

function renderDraftLead(lead) {
    const quote = lead.latest_quote;
    const total = quote ? Number(quote.total).toFixed(2) : '0.00';
    
    // Debug info per campi non mappati
    const normalized = lead.normalized_payload || {};
    const unmappedFields = normalized._unmapped_fields || {};
    const unmappedDebug = Object.keys(unmappedFields).length > 0 
        ? `<details class=\"debug-details\"><summary>📋 ${Object.keys(unmappedFields).length} campi non mappati</summary><pre>${escapeHtml(JSON.stringify(unmappedFields, null, 2))}</pre></details>`
        : '';
    
    return `
        <article class="lead-card">
            <div class="lead-top">
                <h3>${escapeHtml(lead.client_name || 'Cliente non indicato')}</h3>
                <span class="status status-info">Bozza</span>
            </div>
            <p class="lead-meta">Fonte: ${renderSourceLabel(lead.source)}</p>
            <p>${escapeHtml(lead.description || 'Nessuna descrizione')}</p>
            <p class="lead-note">${escapeHtml(lead.review_summary || '')}</p>
            ${unmappedDebug}
            <div class="quote-meta">
                <span>Quote #${quote.id}</span>
                <strong>€${total}</strong>
            </div>
            <div class="card-actions">
                <button onclick="sendQuote(${quote.id})">Invia bozza</button>
            </div>
        </article>
    `;
}

function renderSentLead(lead) {
    const quote = lead.latest_quote;
    return `
        <article class="lead-card">
            <div class="lead-top">
                <h3>${escapeHtml(lead.client_name || 'Cliente non indicato')}</h3>
                <span class="status status-success">Inviato</span>
            </div>
            <p class="lead-meta">Fonte: ${renderSourceLabel(lead.source)}</p>
            <p>${escapeHtml(lead.description || 'Nessuna descrizione')}</p>
            <p class="lead-note">Ultimo preventivo inviato: ${quote ? escapeHtml(quote.sent_at || quote.generated_at || '') : 'n/d'}</p>
        </article>
    `;
}

function renderActivityLog(items) {
    const container = document.getElementById('activity-log');
    document.getElementById('badge-activity').textContent = items.length;

    if (!items.length) {
        container.className = 'activity-list empty-state';
        container.textContent = 'Nessuna attività recente.';
        return;
    }

    container.className = 'activity-list';
    container.innerHTML = items.map(item => `
        <article class="activity-item">
            <div class="activity-top">
                <strong>${escapeHtml(item.event_type)}</strong>
                <span>${escapeHtml(formatDate(item.created_at))}</span>
            </div>
            <p>${escapeHtml(item.message)}</p>
            <small>actor=${escapeHtml(item.actor || 'system')} ${item.lead_id ? `• lead #${escapeHtml(item.lead_id)}` : ''}</small>
        </article>
    `).join('');
}

async function saveReceiver() {
    const email = document.getElementById('new-email').value.trim();
    if (!email || !email.includes('@')) {
        alert('Inserisci un indirizzo email valido.');
        return;
    }

    const response = await fetch('/api/receivers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
    });

    if (!response.ok) {
        alert('Impossibile aggiornare il destinatario.');
        return;
    }

    await loadSummary();
}

async function sendQuote(quoteId) {
    const response = await fetch(`/api/quotes/${quoteId}/send`, { method: 'POST' });

    if (!response.ok) {
        const error = await response.json();
        alert(error.detail || 'Invio non riuscito.');
        return;
    }

    await refreshDashboard();
}

function renderSourceLabel(source) {
    if (!source) return 'n/d';
    return escapeHtml(source.replaceAll('_', ' '));
}

function formatDate(value) {
    if (!value) return 'n/d';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleString('it-IT');
}

function escapeHtml(value) {
    return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}
