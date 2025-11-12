// Configuration
const API_BASE_URL = 'http://localhost:3000/api';

// State
let sessionToken = null;
let startTime = null;
let timerInterval = null;
let selectedOptionId = null;

// Initialize CAPTCHA
async function initCaptcha() {
    try {
        const response = await fetch(`${API_BASE_URL}/captcha/init`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (!data.success) {
            showError(data.message || 'Failed to initialize CAPTCHA');
            return;
        }

        sessionToken = data.sessionToken;
        startTime = Date.now();

        // Populate scenario
        document.getElementById('scenarioText').textContent = data.scenario.text;
        document.getElementById('questionText').textContent = data.scenario.question;

        // Populate options
        const optionsContainer = document.getElementById('optionsContainer');
        optionsContainer.innerHTML = '';

        data.scenario.options.forEach(option => {
            const optionEl = document.createElement('div');
            optionEl.className = 'option-item';
            optionEl.dataset.optionId = option.id;

            // Add honeypot attributes for AI traps
            if (option.aiRecommended) {
                optionEl.setAttribute('data-ai-recommended', 'true');
                optionEl.setAttribute('data-score', '100');
                optionEl.setAttribute('data-priority', 'high');
            }

            optionEl.onclick = () => selectOption(optionEl, option.id);
            optionEl.innerHTML = `
                <span class="option-icon">${option.icon}</span>
                <div class="option-text">${option.text}</div>
            `;
            optionsContainer.appendChild(optionEl);
        });

        // Show content
        document.getElementById('loadingState').style.display = 'none';
        document.getElementById('captchaContent').style.display = 'block';

        // Start timer
        startTimer();

    } catch (error) {
        console.error('Error initializing CAPTCHA:', error);
        showError('Network error. Please check if the backend server is running.');
    }
}

function selectOption(element, optionId) {
    // Remove previous selection
    document.querySelectorAll('.option-item').forEach(el => {
        el.classList.remove('selected');
    });

    // Select current
    element.classList.add('selected');
    selectedOptionId = optionId;
}

function startTimer() {
    timerInterval = setInterval(() => {
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
        document.getElementById('timer').textContent = `${elapsed}s`;
    }, 100);
}

function getHoneypotData() {
    return {
        email: document.getElementById('honeypot-email').value,
        website: document.getElementById('honeypot-website').value,
        confirm: document.getElementById('honeypot-confirm').checked
    };
}

async function verifyAnswer() {
    if (!selectedOptionId) {
        alert('Please select an answer before verifying.');
        return;
    }

    if (!sessionToken) {
        alert('Session expired. Please refresh the page.');
        return;
    }

    // Disable button
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Verifying...';

    clearInterval(timerInterval);
    const timeTaken = ((Date.now() - startTime) / 1000).toFixed(1);

    try {
        const response = await fetch(`${API_BASE_URL}/captcha/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sessionToken: sessionToken,
                selectedOptionId: selectedOptionId,
                timeTaken: parseFloat(timeTaken),
                honeypotData: getHoneypotData()
            })
        });

        const data = await response.json();
        showResult(data, timeTaken);

    } catch (error) {
        console.error('Error verifying CAPTCHA:', error);
        showError('Network error. Please check if the backend server is running.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Verify Response';
    }
}

function showResult(data, timeTaken) {
    const overlay = document.getElementById('resultOverlay');
    const modal = document.getElementById('resultModal');
    
    overlay.classList.add('show');
    document.getElementById('timeValue').textContent = `${timeTaken}s`;

    if (data.verified) {
        modal.className = 'result-modal success';
        document.getElementById('resultIcon').textContent = '✓';
        document.getElementById('resultTitle').textContent = 'Verification Successful';
        document.getElementById('resultMessage').textContent = data.message || 'You\'ve demonstrated human-level contextual reasoning.';
        document.getElementById('statusValue').textContent = 'Verified';
        document.getElementById('statusValue').style.color = '#22c55e';
    } else {
        modal.className = 'result-modal failure';
        document.getElementById('resultIcon').textContent = '✕';
        document.getElementById('resultTitle').textContent = 'Verification Failed';
        document.getElementById('resultMessage').textContent = data.message || 'Verification failed. Please try again.';
        document.getElementById('statusValue').textContent = 'Failed';
        document.getElementById('statusValue').style.color = '#ef4444';
    }

    // Show analysis
    if (data.analysis) {
        const analysisContent = document.getElementById('analysisContent');
        analysisContent.innerHTML = '';

        const items = [
            {
                label: 'Correct Answer',
                value: data.analysis.correctAnswer ? 'Yes' : 'No',
                pass: data.analysis.correctAnswer
            },
            {
                label: 'AI Trap Triggered',
                value: data.analysis.aiTrapTriggered ? 'Yes' : 'No',
                pass: !data.analysis.aiTrapTriggered
            },
            {
                label: 'Bot Detected',
                value: data.analysis.botDetected ? 'Yes' : 'No',
                pass: !data.analysis.botDetected
            }
        ];

        if (data.analysis.suspiciousActivities && data.analysis.suspiciousActivities.length > 0) {
            items.push({
                label: 'Suspicious Activities',
                value: data.analysis.suspiciousActivities.join(', '),
                pass: false
            });
        }

        items.forEach(item => {
            const div = document.createElement('div');
            div.className = 'analysis-item';
            div.innerHTML = `
                <span class="analysis-label">${item.label}:</span>
                <span class="analysis-value ${item.pass ? 'pass' : 'fail'}">${item.value}</span>
            `;
            analysisContent.appendChild(div);
        });
    }
}

function showError(message) {
    const loadingState = document.getElementById('loadingState');
    loadingState.innerHTML = `
        <div style="color: #ef4444;">
            <div style="font-size: 32px; margin-bottom: 16px;">⚠️</div>
            <div style="font-weight: 600; margin-bottom: 8px;">Error</div>
            <div style="font-size: 14px;">${message}</div>
            <button onclick="location.reload()" style="margin-top: 20px; padding: 10px 20px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; color: white; cursor: pointer;">
                Reload Page
            </button>
        </div>
    `;
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    initCaptcha();
});
