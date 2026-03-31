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
    document.getElementById('count-ready').textContent = data.counts.ready_for_quote || 0;
    document.getElementById('count-drafts').textContent = data.counts.draft_quotes || 0;
    document.getElementById('count-sent').textContent = data.counts.sent || 0;
    document.getElementById('count-error').textContent = data.counts.error || 0;

    document.getElementById('badge-incomplete').textContent = data.counts.incomplete || 0;
    document.getElementById('badge-draft').textContent = data.counts.draft_quotes || 0;
    document.getElementById('badge-sent').textContent = data.counts.sent || 0;

    const systemStatus = data.email_enabled
        ? 'Email abilitate: puoi inviare i preventivi dalla dashboard.'
        : 'Email disabilitate: ambiente sicuro/test, nessun invio reale.';

    document.getElementById('system-status').textContent = systemStatus;
    document.getElementById('receiver-current').textContent = `Destinatario attivo: ${data.active_receiver_email}`;
    document.getElementById('new-email').value = data.active_receiver_email || '';
}

async function loadLeads() {
    const response = await fetch('/api/leads');
    const data = await response.json();
    const leads = data.leads || [];

    const incomplete = leads.filter(lead => lead.status === 'incomplete');
    const drafts = leads.filter(lead => lead.latest_quote && lead.latest_quote.status === 'draft');
    const sent = leads.filter(lead => lead.status === 'sent');

    renderLeadList('list-incomplete', incomplete, renderIncompleteLead);
    renderLeadList('list-draft', drafts, renderDraftLead);
    renderLeadList('list-sent', sent, renderSentLead);
}

function renderLeadList(elementId, leads, renderer) {
    const container = document.getElementById(elementId);

    if (!leads.length) {
        container.className = 'lead-list empty-state';
        if (elementId === 'list-incomplete') container.textContent = 'Nessuna richiesta incompleta.';
        if (elementId === 'list-draft') container.textContent = 'Nessuna bozza pronta.';
        if (elementId === 'list-sent') container.textContent = 'Nessun preventivo inviato.';
        return;
    }

    container.className = 'lead-list';
    container.innerHTML = leads.map(renderer).join('');
}

function renderIncompleteLead(lead) {
    const missing = (lead.missing_fields || []).map(field => `<span class="pill warning">${field}</span>`).join('');
    return `
        <article class="lead-card">
            <div class="lead-top">
                <h3>${escapeHtml(lead.client_name || 'Cliente non indicato')}</h3>
                <span class="status status-warning">Incompleto</span>
            </div>
            <p>${escapeHtml(lead.description || 'Nessuna descrizione')}</p>
            <div class="pill-row">${missing}</div>
            <p class="lead-note">${escapeHtml(lead.review_summary || '')}</p>
        </article>
    `;
}

function renderDraftLead(lead) {
    const quote = lead.latest_quote;
    const total = quote ? Number(quote.total).toFixed(2) : '0.00';
    return `
        <article class="lead-card">
            <div class="lead-top">
                <h3>${escapeHtml(lead.client_name || 'Cliente non indicato')}</h3>
                <span class="status status-info">Bozza</span>
            </div>
            <p>${escapeHtml(lead.description || 'Nessuna descrizione')}</p>
            <p class="lead-note">${escapeHtml(lead.review_summary || '')}</p>
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
            <p>${escapeHtml(lead.description || 'Nessuna descrizione')}</p>
            <p class="lead-note">Ultimo preventivo inviato: ${quote ? escapeHtml(quote.sent_at || quote.generated_at || '') : 'n/d'}</p>
        </article>
    `;
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

function escapeHtml(value) {
    return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}
