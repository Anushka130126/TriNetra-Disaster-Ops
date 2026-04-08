// ==========================================
// 1. INITIALIZATION: MAP & CHART
// ==========================================

// Initialize Map (Dark Theme CartoDB)
const map = L.map('map', { zoomControl: false }).setView([20.5937, 78.9629], 5);
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap &copy; CARTO'
}).addTo(map);

let currentMarker = null;

// Initialize Chart (With smooth red gradient)
const ctx = document.getElementById('severityChart').getContext('2d');
const severityChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Step 0'],
        datasets: [{
            label: 'Severity Level',
            data: [0],
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.1)', // Smooth gradient fill
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#ef4444'
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: { beginAtZero: true, max: 1.0, grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
            x: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } }
        },
        plugins: { legend: { display: false } }
    }
});

// ==========================================
// 2. DASHBOARD UPDATER ENGINE
// ==========================================

let lastStepSeen = -1;
let currentRegionTracker = "";
let isOverrideActive = false; // Add this variable globally

function updateDashboard(state) {
    // 1. Bulletproof Task-Switch Detection
    if (state.region && state.region !== currentRegionTracker) {
        if (currentRegionTracker !== "") {
            // Add a visual divider in the terminal for the new region
            const term = document.getElementById('terminal-output');
            const entry = document.createElement('div');
            entry.style.cssText = "color: var(--text-muted); margin: 15px 0; border-top: 1px dashed var(--border); padding-top: 10px; text-align: center; font-size: 0.7rem; font-weight: bold;";
            entry.innerText = `SYSTEM RECALIBRATING: ${state.region.toUpperCase()}`;
            term.appendChild(entry);
            term.scrollTop = term.scrollHeight;
        }
        currentRegionTracker = state.region;
        lastStepSeen = -1; // Force reset the step memory for new scenario
    }

    // 2. Text Telemetry Updates
    document.getElementById('ui-region').innerText = state.region || "--";
    document.getElementById('ui-weather').innerText = (state.forecast || "--").toUpperCase();
    document.getElementById('ui-severity').innerText = state.severity !== undefined ? `${(state.severity * 100).toFixed(0)}%` : "--%";
    document.getElementById('ui-pop').innerText = state.population ? state.population.toLocaleString() : "--";
    document.getElementById('ui-cas').innerText = state.casualties || 0;
    document.getElementById('ui-step').innerText = `STEP ${state.step || 0}/3`;
    document.getElementById('ui-budget').innerText = state.budget !== undefined ? `$${state.budget.toLocaleString()}` : "$0";

    // Resources
    if (state.resources) {
        document.getElementById('ui-boats').innerText = state.resources.boats;
        document.getElementById('ui-amb').innerText = state.resources.ambulances;
        document.getElementById('ui-kits').innerText = state.resources.food_kits;
    }

    // 3. Dynamic Map Updates
    if (state.coords && state.coords.length === 2) {
        if (currentMarker) map.removeLayer(currentMarker);

        // Color logic based on severity
        let markerColor = '#ef4444'; // Red (Critical)
        if (state.severity <= 0.4) markerColor = '#22c55e'; // Green (Secured / Efficiently Handled)
        else if (state.severity <= 0.7) markerColor = '#f59e0b'; // Orange (Elevated Risk)

        currentMarker = L.circleMarker(state.coords, {
            radius: 12,
            fillColor: markerColor,
            color: markerColor,
            weight: 2,
            opacity: 1,
            fillOpacity: 0.6
        }).addTo(map);

        map.flyTo(state.coords, 6, { duration: 1.5 });
    }

    // 4. Chart Updates
    if (state.history) {
        severityChart.data.labels = state.history.map(h => `Step ${h.step}`);
        severityChart.data.datasets[0].data = state.history.map(h => h.severity);
        severityChart.update();
    }

    // 5. Action Logging
    if (state.last_action && state.step !== lastStepSeen) {
        lastStepSeen = state.step; // Lock in the new step

        // Update Score and Feedback UI
        const scoreUI = document.getElementById('ui-score');
        scoreUI.innerText = state.last_action.score.toFixed(2);

        // Change score color based on success
        if (state.last_action.score >= 0.8) scoreUI.style.color = "var(--success)";
        else if (state.last_action.score >= 0.5) scoreUI.style.color = "var(--warning)";
        else scoreUI.style.color = "var(--danger)";

        if (state.last_action.feedback && state.last_action.feedback.length > 0) {
            document.getElementById('ui-feedback').innerText = state.last_action.feedback[0];
        }

        const type = isOverrideActive ? "human" : "agent";
        logToTerminal(`Deployed to ${state.last_action.target_region} | Threat: ${state.last_action.decision}`, type);
    }
}

// ==========================================
// 3. TERMINAL AND WEBSOCKET LOGIC
// ==========================================

function logToTerminal(message, type = "system") {
    const term = document.getElementById('terminal-output');
    const time = new Date().toLocaleTimeString('en-GB'); // 24-hour format

    let color = "#94a3b8"; // Default system gray
    let prefix = "[SYSTEM]";

    if (type === "agent") {
        color = "#3b82f6"; // Blue
        prefix = "[AGENT]";
    } else if (type === "human") {
        color = "#f59e0b"; // Orange
        prefix = "[HUMAN]";
    }

    const entry = document.createElement('div');
    entry.style.marginBottom = "4px";
    entry.innerHTML = `<span style="color: #64748b;">${time}</span> <span style="color: ${color}; font-weight: bold;">${prefix}</span> <span style="color: #e2e8f0;">${message}</span>`;

    term.appendChild(entry);
    term.scrollTop = term.scrollHeight; // Auto-scroll to bottom
}

// Clock logic
setInterval(() => {
    document.getElementById('clock').innerText = new Date().toLocaleTimeString('en-GB');
}, 1000);

// WebSocket Connection (Connects to your FastAPI Backend)
function connectWebSocket() {
    const ws = new WebSocket(`ws://${window.location.host}/ws`);

    ws.onopen = () => {
        logToTerminal("WebSocket established. Streaming live telemetry.", "system");
    };

    ws.onmessage = (event) => {
        const state = JSON.parse(event.data);
        updateDashboard(state);
    };

    ws.onclose = () => {
        logToTerminal("Connection lost. Reconnecting in 3s...", "system");
        setTimeout(connectWebSocket, 3000);
    };
}

// ==========================================
// 4. HUMAN COMMAND PROTOCOL (MANUAL OVERRIDE)
// ==========================================

function toggleOverride() {
    isOverrideActive = !isOverrideActive;
    const btn = document.getElementById('btn-override');
    const panel = document.getElementById('override-panel');
    const telemetryPanel = document.getElementById('telemetry-panel');

    if (isOverrideActive) {
        btn.innerText = "MANUAL OVERRIDE: ON";
        btn.classList.remove('btn-warning');
        btn.style.backgroundColor = "var(--danger)";
        btn.style.color = "white";
        btn.style.borderColor = "var(--danger)";

        panel.style.display = "block";
        telemetryPanel.style.opacity = "0.3"; // Dim telemetry to focus on controls
        logToTerminal("MANUAL OVERRIDE PROTOCOL ACTIVATED", "human");
    } else {
        btn.innerText = "MANUAL OVERRIDE: OFF";
        btn.style.backgroundColor = ""; // Reset to default CSS
        btn.style.color = "";
        btn.style.borderColor = "";
        btn.classList.add('btn-warning');

        panel.style.display = "none";
        telemetryPanel.style.opacity = "1.0";
        logToTerminal("Manual override disengaged. AI Swarm resumed.", "system");
    }
}

async function submitManualAction() {
    if (!isOverrideActive) return;

    // Grab values from the UI
    const threat = document.getElementById('man-threat').value;
    const region = document.getElementById('man-region').value || "Unknown Region";
    const boats = parseInt(document.getElementById('man-boats').value) || 0;
    const amb = parseInt(document.getElementById('man-amb').value) || 0;

    // Create the exact JSON schema the backend expects
    const payload = {
        threat_level: threat,
        deploy_region: region,
        budget_scratchpad: "HUMAN OVERRIDE INITIATED. Budget constraints bypassed.",
        resource_allocation: {
            boats: boats,
            ambulances: amb,
            food_kits: 0
        },
        reasoning: "Human Commander Override Directive Executed."
    };

    logToTerminal(`Transmitting manual orders to ${region}...`, "human");

    try {
        // Send to FastAPI backend
        const response = await fetch('/step', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error("Server rejected action");
        logToTerminal(`Directives confirmed by field assets.`, "system");

        // Clear the form after sending
        document.getElementById('man-region').value = "";
        document.getElementById('man-boats').value = 0;
        document.getElementById('man-amb').value = 0;

    } catch (error) {
        logToTerminal(`TRANSMISSION FAILED: ${error.message}`, "system");
    }
}

async function resetEnv() {
    logToTerminal("INITIATING FORCE RESET...", "system");
    try {
        // Ping the FastAPI reset endpoint for the default scenario
        await fetch('/reset?scenario_id=triage_basic');
        logToTerminal("ENVIRONMENT RESET SUCCESSFUL", "system");
    } catch (error) {
        logToTerminal(`RESET CONNECTION FAILED`, "system");
    }
}

// Start everything up
window.onload = () => {
    connectWebSocket();
};