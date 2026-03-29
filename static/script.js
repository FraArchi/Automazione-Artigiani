document.addEventListener('DOMContentLoaded', () => {
    loadReceivers();
});

async function loadReceivers() {
    const list = document.getElementById('receiver-list');
    list.innerHTML = '<li>Caricamento...</li>';

    try {
        const response = await fetch('/api/receivers');
        const data = await response.json();
        
        list.innerHTML = '';
        data.receivers.forEach(email => {
            const li = document.createElement('li');
            li.innerHTML = `
                <span>${email}</span>
                <button class="btn-delete" onclick="deleteReceiver('${email}')">Elimina</button>
            `;
            list.appendChild(li);
        });

        if (data.receivers.length === 0) {
            list.innerHTML = '<li>Nessun ricevitore configurato.</li>';
        }
    } catch (error) {
        list.innerHTML = '<li>Errore nel caricamento.</li>';
    }
}

async function addReceiver() {
    const input = document.getElementById('new-email');
    const email = input.value.trim();

    if (!email || !email.includes('@')) {
        alert('Inserisci un indirizzo email valido.');
        return;
    }

    try {
        const response = await fetch('/api/receivers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });

        if (response.ok) {
            input.value = '';
            loadReceivers();
        }
    } catch (error) {
        alert('Errore nell\'aggiunta del ricevitore.');
    }
}

async function deleteReceiver(email) {
    if (!confirm(`Sei sicuro di voler eliminare ${email}?`)) return;

    try {
        const response = await fetch(`/api/receivers/${email}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadReceivers();
        }
    } catch (error) {
        alert('Errore nell\'eliminazione.');
    }
}
