let currentDocument = null;
let loadedDocuments = [];

document.addEventListener('DOMContentLoaded', function () {
    setupEventListeners();
    loadDocumentsList();
});

function setupEventListeners() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const chatInput = document.getElementById('chatInput');

    uploadArea.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', handleFileSelect);

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        handleFileUpload(file);
    }
}

async function handleFileUpload(file) {
    const docName = document.getElementById('docName').value;
    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_name', docName || file.name);

    showLoading();

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            showToast('Document uploaded successfully!', 'success');
            document.getElementById('docName').value = '';
            loadDocumentsList();
        } else {
            showToast(data.error || 'Upload failed', 'error');
        }
    } catch (error) {
        showToast('Error uploading file: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function loadDocumentsList() {
    try {
        const response = await fetch('/api/documents');
        const data = await response.json();

        loadedDocuments = data.documents;
        const listContainer = document.getElementById('documentList');

        if (loadedDocuments.length === 0) {
            listContainer.innerHTML = '<p class="empty-state">No documents loaded yet</p>';
            return;
        }

        listContainer.innerHTML = loadedDocuments.map((doc, index) => `
            <div class="document-item ${index === 0 ? 'active' : ''}" onclick="selectDocument('${doc.name}')">
                <h4><i class="fas fa-file-alt"></i> ${doc.name}</h4>
                <p>${doc.loaded_at} • ${Math.round(doc.length / 1000)}K chars</p>
            </div>
        `).join('');

        if (loadedDocuments.length > 0 && !currentDocument) {
            currentDocument = loadedDocuments[0].name;
        }
    } catch (error) {
        console.error('Error loading documents:', error);
    }
}

function selectDocument(docName) {
    currentDocument = docName;
    document.querySelectorAll('.document-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.closest('.document-item').classList.add('active');
}

async function analyzeDocument() {
    if (!currentDocument) {
        showToast('Please upload a document first', 'error');
        return;
    }

    showLoading();

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ doc_name: currentDocument })
        });

        const data = await response.json();

        if (data.success) {
            displayResult('Analysis', data.analysis, 'fa-search');
        } else {
            showToast(data.error || 'Analysis failed', 'error');
        }
    } catch (error) {
        showToast('Error analyzing document: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function getConcerns() {
    if (!currentDocument) {
        showToast('Please upload a document first', 'error');
        return;
    }

    showLoading();

    try {
        const response = await fetch('/api/concerns', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ doc_name: currentDocument })
        });

        const data = await response.json();

        if (data.success) {
            displayConcerns(data.concerns);
        } else {
            showToast(data.error || 'Failed to get concerns', 'error');
        }
    } catch (error) {
        showToast('Error getting concerns: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function compareDocuments() {
    if (loadedDocuments.length < 2) {
        showToast('Please load at least 2 documents to compare', 'error');
        return;
    }

    const doc1 = prompt('Enter first document name:', loadedDocuments[0].name);
    const doc2 = prompt('Enter second document name:', loadedDocuments[1].name);

    if (!doc1 || !doc2) return;

    showLoading();

    try {
        const response = await fetch('/api/compare', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ doc1, doc2 })
        });

        const data = await response.json();

        if (data.success) {
            displayResult('Document Comparison', data.comparison, 'fa-columns');
        } else {
            showToast(data.error || 'Comparison failed', 'error');
        }
    } catch (error) {
        showToast('Error comparing documents: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function savePDF() {
    const filename = prompt('Enter filename (optional):');

    showLoading();

    try {
        const response = await fetch('/api/save-pdf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: filename || null })
        });

        const data = await response.json();

        if (data.success) {
            showToast('PDF saved successfully!', 'success');
            window.open(`/api/download/${data.filename}`, '_blank');
        } else {
            showToast(data.error || 'Failed to save PDF', 'error');
        }
    } catch (error) {
        showToast('Error saving PDF: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message) return;

    addMessage(message, 'user');
    input.value = '';

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                doc_name: currentDocument
            })
        });

        const data = await response.json();

        if (data.success) {
            addMessage(data.response, 'bot');
        } else {
            addMessage('Error: ' + (data.error || 'Failed to get response'), 'bot');
        }
    } catch (error) {
        addMessage('Error: ' + error.message, 'bot');
    }
}

async function clearChat() {
    try {
        await fetch('/api/clear', { method: 'POST' });
        document.getElementById('chatMessages').innerHTML = '';
        showToast('Chat cleared', 'success');
    } catch (error) {
        showToast('Error clearing chat: ' + error.message, 'error');
    }
}

function displayResult(title, content, icon) {
    const resultsArea = document.getElementById('resultsArea');
    resultsArea.innerHTML = `
        <div class="result-card">
            <h3><i class="fas ${icon}"></i> ${title}</h3>
            <p>${content}</p>
        </div>
    `;
}

function displayConcerns(concerns) {
    const resultsArea = document.getElementById('resultsArea');

    if (concerns.length === 0) {
        resultsArea.innerHTML = `
            <div class="result-card">
                <h3><i class="fas fa-check-circle" style="color: var(--secondary);"></i> No Major Concerns</h3>
                <p>The document appears to be relatively standard without any major red flags.</p>
            </div>
        `;
        return;
    }

    const concernsHTML = concerns.map(concern => {
        const severityClass = concern.severity.toLowerCase();
        const emoji = severityClass === 'high' ? '🔴' : severityClass === 'medium' ? '🟡' : '🟢';

        return `
            <div class="concern-card ${severityClass}">
                <div class="concern-header">
                    <span>${emoji}</span>
                    <span class="severity-badge ${severityClass}">${concern.severity}</span>
                </div>
                <p style="margin-bottom: 10px;"><strong>Clause:</strong> "${concern.clause}"</p>
                <p style="margin-bottom: 10px;"><strong>Concern:</strong> ${concern.concern}</p>
                <p><strong>Recommendation:</strong> ${concern.recommendation}</p>
            </div>
        `;
    }).join('');

    resultsArea.innerHTML = `
        <div class="result-card">
            <h3><i class="fas fa-exclamation-triangle"></i> Found ${concerns.length} Concerning Clause(s)</h3>
        </div>
        ${concernsHTML}
    `;
}

function addMessage(content, type) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.innerHTML = `<div class="message-content">${content}</div>`;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}
function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

async function loadSampleDocument() {
    showLoading();
    try {
        const response = await fetch('/static/sample-legal-document.txt');
        const blob = await response.blob();
        const file = new File([blob], 'sample-legal-document.txt', { type: 'text/plain' });

        document.getElementById('docName').value = 'Sample Document';
        await handleFileUpload(file);
    } catch (error) {
        showToast('Error loading sample document: ' + error.message, 'error');
        hideLoading();
    }
}