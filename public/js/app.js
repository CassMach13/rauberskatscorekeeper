// public/js/app.js

// API URL - Change this for production if needed
// API URL - Relative path allows access from any network interface (localhost or IP)
const API_URL = '';
let currentGameId = null;
let currentGameState = null; // Store latest state for export

// DOM Elements
const startGameBtn = document.getElementById('start-game-btn');
const messageDiv = document.getElementById('message');
const setupScreen = document.getElementById('setup-screen');
const gameScreen = document.getElementById('game-screen');
const endScreen = document.getElementById('end-screen');
const calculateBtn = document.getElementById('calculate-btn');
const undoBtn = document.getElementById('undo-btn');
const endGameBtn = document.getElementById('end-game-btn');
const playAgainBtn = document.getElementById('play-again-btn');
const exportBtn = document.getElementById('export-btn'); // New
const finalResultsDiv = document.getElementById('final-results');

const newPlayForm = document.getElementById('new-play-form');
const comboJogador = document.getElementById('combo-jogador');
const comboJogo = document.getElementById('combo-jogo');

// --- Initialization ---

document.addEventListener('DOMContentLoaded', function () {
    // Initialize date pickers
    if (typeof flatpickr !== 'undefined') {
        flatpickr("#game-date", { dateFormat: "d/m/Y", defaultDate: "today", locale: "pt" });
        flatpickr("#start-time", { enableTime: true, noCalendar: true, dateFormat: "H:i", time_24hr: true, defaultDate: new Date() });
        flatpickr("#end-time", { enableTime: true, noCalendar: true, dateFormat: "H:i", time_24hr: true, defaultDate: "00:00" });
    }

    // Event Listeners
    startGameBtn.addEventListener('click', startGame);
    calculateBtn.addEventListener('click', calculateScore);
    undoBtn.addEventListener('click', undoLastMove);
    endGameBtn.addEventListener('click', endGame);
    playAgainBtn.addEventListener('click', () => {
        // Clear URL and reload to start fresh
        window.location.href = window.location.pathname;
    });
    exportBtn.addEventListener('click', exportResults);

    const exportHtmlBtn = document.getElementById('export-html-btn');
    if (exportHtmlBtn) {
        exportHtmlBtn.addEventListener('click', () => {
            console.log("Export HTML Clicked"); // Debug
            if (!currentGameState) {
                console.error("No currentGameState found!");
                return;
            }
            // Use the function defined later
            generateHTMLReportWrapper();
        });
    }

    // Form Interactions
    document.getElementById('num-players').addEventListener('change', togglePlayer4);
    comboJogo.addEventListener('change', updateFormVisibility);

    // Dynamic Form Updates (Defined here to be safe)
    const triggers = [
        'check-houve-empate', 'check-schneider', 'check-schwartz',
        'check-kontra', 'check-reh', 'check-bock'
    ];
    triggers.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('change', () => updateFormVisibility());
    });

    comboJogador.addEventListener('change', (e) => updateTiePlayerDropdown(e.target.value));

    // Initial State
    updateFormVisibility();

    // Feature: Persistence via URL
    const urlParams = new URLSearchParams(window.location.search);
    const existingGameId = urlParams.get('game_id');
    if (existingGameId) {
        console.log("Found Game ID in URL:", existingGameId);
        currentGameId = existingGameId;
        fetchAndRenderGameState(existingGameId);
    } else {
        console.log("App initialized - No active game");
    }
});


// --- Actions ---

async function startGame() {
    console.log("Starting game...");
    const numPlayers = parseInt(document.getElementById('num-players').value, 10);
    let playerNames = [
        document.getElementById('player1').value.trim(),
        document.getElementById('player2').value.trim(),
        document.getElementById('player3').value.trim()
    ];

    if (numPlayers === 4) {
        playerNames.push(document.getElementById('player4').value.trim());
    }

    if (playerNames.some(name => name === '')) {
        showMessage('Por favor, preencha o nome de todos os jogadores.', 'error');
        return;
    }

    const gameDetails = {
        player_names: playerNames,
        date: document.getElementById('game-date').value,
        venue: document.getElementById('game-venue').value,
        table: document.getElementById('game-table').value,
        start_time: document.getElementById('start-time').value,
        end_time: document.getElementById('end-time').value
    };

    console.log("Game Details:", gameDetails);

    if (!gameDetails.venue || !gameDetails.date) {
        showMessage('Preencha a Data e a Sede.', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/start_game`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(gameDetails)
        });
        const result = await response.json();

        if (response.ok) {
            currentGameId = result.game_id;
            console.log("Game started, ID:", currentGameId);

            // Persistence: Update URL without reload
            const newUrl = `${window.location.pathname}?game_id=${currentGameId}`;
            window.history.pushState({ path: newUrl }, '', newUrl);

            await fetchAndRenderGameState(currentGameId);
        } else {
            console.error("Error starting game:", result.error);
            showMessage(result.error || 'Erro ao criar jogo.', 'error');
        }
    } catch (error) {
        console.error("Network error:", error);
        showMessage('Erro de conexão com o servidor.', 'error');
    }
}

async function calculateScore() {
    console.log("Calculating score...");
    // Disable button to prevent double clicks
    calculateBtn.disabled = true;
    calculateBtn.textContent = 'Calculando...';

    const dados = {
        jogador: document.getElementById('combo-jogador').value,
        jogo: document.getElementById('combo-jogo').value,
        com_sem: document.getElementById('combo-com-sem').value,
        pontos_ramsch: document.getElementById('input-pontos-ramsch').value,
        hand: document.getElementById('check-hand').checked,
        ouvert: document.getElementById('check-ouvert').checked,
        schneider: document.getElementById('check-schneider').checked,
        schneider_anunciado: document.getElementById('check-schneider-anunciado').checked,
        schwartz: document.getElementById('check-schwartz').checked,
        schwartz_anunciado: document.getElementById('check-schwartz-anunciado').checked,
        kontra: document.getElementById('check-kontra').checked,
        reh: document.getElementById('check-reh').checked,
        bock: document.getElementById('check-bock').checked,
        rursch: document.getElementById('check-rursch').checked,
        jungfrau: document.getElementById('check-jungfrau').checked,
        perdeu: document.getElementById('check-perdeu').checked,
        houve_empate: document.getElementById('check-houve-empate').checked,
        empates: document.getElementById('check-houve-empate').checked ? document.getElementById('combo-jogador-empate').value : null,
        info: {
            skat_empurrado: parseInt(document.getElementById('combo-skat-empurrado').value) || 0
        }
    };

    if (!dados.jogador || !dados.jogo) {
        alert('Selecione Jogador e Jogo.');
        calculateBtn.disabled = false;
        calculateBtn.textContent = 'Calcular Pontos';
        return;
    }

    // Validation for Com/Sem if visible
    const comSemVisible = document.getElementById('combo-com-sem').offsetParent !== null;
    if (comSemVisible && !dados.com_sem) {
        alert('Por favor, selecione "Com ou Sem".');
        calculateBtn.disabled = false;
        calculateBtn.textContent = 'Calcular Pontos';
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/game/${currentGameId}/calculate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados)
        });
        const updatedGameState = await response.json();

        if (response.ok) {
            renderGameState(updatedGameState);
        } else {
            console.error("Calculation error:", updatedGameState.error);
            showMessage(updatedGameState.error || 'Erro ao calcular.', 'error');
        }
    } catch (error) {
        console.error("Network error:", error);
        showMessage(error.message, 'error');
    } finally {
        // Re-enable button
        calculateBtn.disabled = false;
        calculateBtn.textContent = 'Calcular Pontos';
    }
}

async function undoLastMove() {
    if (!confirm('Desfazer a última jogada?')) return;

    try {
        const response = await fetch(`${API_URL}/api/game/${currentGameId}/undo`, { method: 'POST' });
        const result = await response.json();
        if (response.ok) {
            renderGameState(result);
            showMessage('Jogada desfeita!', 'success');
        } else {
            showMessage(result.error, 'error');
        }
    } catch (e) {
        showMessage(e.message, 'error');
    }
}

async function endGame() {
    if (!confirm('Finalizar o jogo?')) return;

    try {
        const response = await fetch(`${API_URL}/api/game/${currentGameId}`);
        const finalState = await response.json();

        if (!response.ok) throw new Error(finalState.error);

        document.body.classList.remove('game-active'); // Disable fixed layout
        gameScreen.style.display = 'none';
        endScreen.style.display = 'block';

        const scores = finalState.scores;
        const names = Object.keys(scores);
        const maxScore = Math.max(...Object.values(scores));
        const winners = names.filter(n => scores[n] === maxScore);

        let html = `<h3>Vencedor(es): ${winners.join(', ')} 🏆</h3>`;
        html += `<p>Score Máximo: ${maxScore}</p>`;

        // Pagamentos
        html += '<div style="margin-top: 20px; text-align: left; display: inline-block;"><h4>Pagamentos ao Caixa:</h4>';
        names.forEach(name => {
            if (!winners.includes(name)) {
                const diff = maxScore - scores[name];
                const pay = diff * 0.05;
                html += `<p>${name}: R$ ${pay.toFixed(2).replace('.', ',')}</p>`;
            }
        });
        html += '</div>';

        finalResultsDiv.innerHTML = html;

    } catch (e) {
        showMessage(e.message, 'error');
    }
}

function exportResults() {
    if (!currentGameId) return;
    // Simple JSON export for now
    fetch(`${API_URL}/api/game/${currentGameId}`)
        .then(r => r.json())
        .then(data => {
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Rauberskat_Game_${currentGameId}.json`;
            a.click();
        });
}


// --- Rendering & Logic ---

async function fetchAndRenderGameState(gameId) {
    try {
        const res = await fetch(`${API_URL}/api/game/${gameId}`);
        const data = await res.json();
        if (res.ok) renderGameState(data);
        else showMessage(data.error, 'error');
    } catch (e) {
        showMessage(e.message, 'error');
    }
}

function renderGameState(gameState) {
    currentGameState = gameState; // Update global state reference
    console.log("Rendering state:", gameState);
    document.body.classList.add('game-active'); // Enable fixed layout
    setupScreen.style.display = 'none';
    messageDiv.style.display = 'none';
    gameScreen.style.display = 'grid';

    document.getElementById('current-round').textContent = gameState.current_mode;
    document.getElementById('current-dealer').textContent = gameState.player_names[gameState.dealer_index];

    renderScoreboard(gameState);

    // Log
    const lastPlay = gameState.game_history.length > 0 ? gameState.game_history[gameState.game_history.length - 1] : null;
    if (lastPlay) {
        document.getElementById('last-play-log-container').style.display = 'block';
        renderLastPlayLog(lastPlay);
    }

    handleRamschDecision(gameState);
    populateDropdowns(gameState);

    newPlayForm.reset();
    updateFormVisibility();
}

function renderScoreboard(gameState) {
    const header = document.getElementById('scoreboard-header');
    const body = document.getElementById('scoreboard-body');
    header.innerHTML = '<th>#</th>';
    body.innerHTML = '';

    // Ranking Logic
    const playerScores = gameState.player_names.map(name => ({ name, score: gameState.scores[name] }));
    playerScores.sort((a, b) => b.score - a.score);

    const ranks = {};
    let currentRank = 1;

    playerScores.forEach((p, i) => {
        if (i > 0 && p.score < playerScores[i - 1].score) {
            currentRank++;
        }
        ranks[p.name] = currentRank;
    });

    gameState.player_names.forEach(name => {
        const th = document.createElement('th');
        const rank = ranks[name];
        const totalScore = gameState.scores[name] || 0;

        let scoreColor = '#fff'; // Default zero
        if (totalScore > 0) scoreColor = '#4ade80'; // Green
        if (totalScore < 0) scoreColor = '#f87171'; // Red

        if (rank === 1) th.classList.add('rank-gold');
        if (rank === 2) th.classList.add('rank-silver');
        if (rank === 3) th.classList.add('rank-bronze');

        th.innerHTML = `
            <div class="header-name">${name}</div>
            <div class="header-score" style="color: ${scoreColor}">${totalScore}</div>
            <div class="player-rank">${rank}º</div>
        `;
        header.appendChild(th);
    });
    header.innerHTML += '<th>Spiel</th>';

    // Rows
    const initialScores = {};
    gameState.player_names.forEach(n => initialScores[n] = 0);
    let cumulative = { ...initialScores };

    gameState.game_history.forEach((play, idx) => {
        const points = play.result.points;
        const scorer = play.jogador;

        cumulative[scorer] += points;
        if (play.jogo === 'ramsch' && play.houve_empate && play.empates) {
            // Empates logic handles simple string or array in backend, adapt here ideally
            const empatePlayer = play.empates;
            cumulative[empatePlayer] += points;
        }

        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${idx + 1}</td>`;

        const isEmpateScorer = (name) => play.jogo === 'ramsch' && play.houve_empate && play.empates === name;

        gameState.player_names.forEach(name => {
            const score = cumulative[name];
            const isScorer = name === scorer || isEmpateScorer(name);
            const scoreClass = score > 0 ? 'score-positive' : (score < 0 ? 'score-negative' : 'score-zero');
            const bgClass = isScorer ? ' highlight-scorer' : '';
            tr.innerHTML += `<td class="${scoreClass}${bgClass}">${score}</td>`;
        });

        // Spiel Column
        let spielText = (points > 0 ? '+' : '') + points;
        let suffix = '';
        if (play.round_mode === 'Bock') suffix = ' B';
        if (play.round_mode === 'Ramsch') {
            if (play.jogo === 'grand hand') {
                suffix = ' <span style="position: relative; display: inline-block; padding: 0 2px; background: linear-gradient(to top right, transparent calc(50% - 1px), #f00 calc(50% - 1px), #f00 calc(50% + 1px), transparent calc(50% + 1px));">GH</span>';
            } else {
                suffix = ' R';
            }
        }

        const spielClass = points > 0 ? 'score-positive' : 'score-negative';
        tr.innerHTML += `<td class="${spielClass}">${spielText}<span style="color:white; font-weight:normal">${suffix}</span></td>`;

        body.appendChild(tr);
    });
}

function renderLastPlayLog(play) {
    console.log("Rendering log for:", play);
    const el = document.getElementById('last-play-log');
    if (!play || !play.result) {
        el.innerHTML = '<em>Nenhuma jogada registrada.</em>';
        return;
    }

    const r = play.result;

    // Style mimicking CMD: Strict Monospace, tight lines
    const lineStyle = 'display: block; margin: 0; padding: 0; line-height: 1.3; font-family: "Consolas", "Monaco", "Courier New", monospace; font-size: 14px; color: #ccc; white-space: pre;';
    const indent = '&nbsp;&nbsp;&nbsp;';

    // Helper to generate a line
    const line = (content) => `<div style="${lineStyle}">${content}</div>`;

    let html = '';

    html += line(`🎯 Dealer: <span style="color:#fff">${play.dealer || '-'}</span>`);
    html += line(`🔄 Rodada: <span style="color:#fff">${play.round_mode || '-'}</span>`);
    html += line(`👤 Jogador: <span style="color:#fff">${play.jogador}</span>`);
    html += line(`🃏 Jogo: <span style="color:#fff">${play.jogo.toUpperCase()}</span>`);

    // Standard modifiers (Check ROOT properties, not info parameter)
    if (play.com_sem) {
        const val = parseInt(play.com_sem, 10);
        html += line(`${indent}📝 Com/Sem: ${val} (fator base: ${val + 1})`);
    }

    const item = (c, i, t) => c ? line(`${indent}${i} ${t}`) : '';

    html += item(play.hand, '✋', 'Hand (+1)');
    html += item(play.ouvert, '👐', 'Ouvert (+1)');
    html += item(play.schneider, '🎯', 'Schneider (+1)');
    html += item(play.schneider_anunciado, '📢', 'Schneider anunciado (+1)');
    html += item(play.schwartz, '⚫', 'Schwarz (+1)');
    html += item(play.schwartz_anunciado, '📢', 'Schwarz anunciado (+1)');

    html += item(play.kontra, '⚔️', 'KONTRA!');
    html += item(play.reh, '🔥', 'REH!');
    html += item(play.bock, '💥', 'BOCK!');
    html += item(play.rursch, '🌪️', 'RURSCH!');
    html += item(play.jungfrau, '🛡️', 'Jüngfrau!');

    // Ramsch specifics
    if (play.jogo === 'ramsch') {
        if (play.houve_empate) {
            html += line(`${indent}🤝 Houve Empate (com ${play.empates})`);
        }
        // skat_empurrado IS inside info object structure in frontend submission
        if (play.info && play.info.skat_empurrado > 0) {
            html += line(`${indent}🃏 Skat Empurrado: ${play.info.skat_empurrado}x`);
        }
    }

    // Bock Active Logic
    if (play.round_mode === 'Bock' && play.jogo !== 'ramsch' && play.jogo !== 'null') {
        html += line(`${indent}🔥 Bock ativo (x2)`);
    }

    html += item(play.perdeu, '❌', 'PERDEU (fator x2 e negativo)');

    html += line(`${indent}📝 Pontos base: ${r.base_score}`);
    html += line(`${indent}🔢 Fator Total: ${r.total_factor}`);

    const arrow = r.points >= 0 ? '➡️ ' : '➡️ ';
    const scoreColor = r.points >= 0 ? '#2ecc71' : '#e74c3c';
    html += line(`${indent}${arrow} <span style="color:${scoreColor}; font-weight:bold">Pontos finais para ${play.jogador}: ${r.points}</span>`);

    el.innerHTML = html;
}

function updateFormVisibility() {
    const game = document.getElementById('combo-jogo').value.toLowerCase();

    // Hide all initially
    document.querySelectorAll('[data-field]').forEach(el => el.style.display = 'none');

    const show = (ids) => ids.forEach(id => {
        const el = document.querySelector(`[data-field="${id}"]`);
        if (el) el.style.display = 'block';
    });

    if (['ouros', 'copas', 'espadas', 'paus', 'grand'].includes(game)) {
        show(['com_sem', 'hand', 'ouvert', 'schneider', 'kontra', 'perdeu']);

        if (document.getElementById('check-schneider').checked) show(['schneider_anunciado', 'schwartz']);
        if (document.getElementById('check-schwartz').checked) show(['schwartz_anunciado']);

        if (document.getElementById('check-kontra').checked) show(['reh']);
        if (document.getElementById('check-reh').checked) show(['bock']);
        if (document.getElementById('check-bock').checked) show(['rursch']);
    }
    else if (game === 'null' || game === 'null revolution') {
        const fields = ['kontra', 'perdeu'];
        if (game === 'null') fields.push('hand', 'ouvert');
        show(fields);

        if (document.getElementById('check-kontra').checked) show(['reh']);
        if (document.getElementById('check-reh').checked) show(['bock']);
        if (document.getElementById('check-bock').checked) show(['rursch']);
    }
    else if (game === 'ramsch') {
        show(['pontos_ramsch', 'jungfrau', 'houve_empate', 'skat_empurrado']);
        if (document.getElementById('check-houve-empate').checked) {
            show(['jogador_que_empatou']);
        }
    }
    else if (game === 'grand hand') {
        show(['com_sem', 'ouvert', 'schneider', 'kontra', 'perdeu']);
    }
}

function showMessage(msg, type) {
    messageDiv.textContent = msg;
    messageDiv.className = type; // 'error' or 'success'
    messageDiv.style.display = 'block';
    setTimeout(() => messageDiv.style.display = 'none', 5000);
}

// Helpers
function togglePlayer4() {
    const val = document.getElementById('num-players').value;
    const p4 = document.querySelector('[data-player-field="4"]');
    p4.style.display = val === '4' ? 'block' : 'none';
}

function updateTiePlayerDropdown(selectedPlayer) {
    const tieSelect = document.getElementById('combo-jogador-empate');
    tieSelect.innerHTML = '';
    const allOptions = document.getElementById('combo-jogador').options;
    for (let opt of allOptions) {
    }
}

// --- Export Logic ---

// Wrapper to call from the main listener
function generateHTMLReportWrapper() {
    if (!currentGameState) return;
    const htmlContent = generateHTMLReport(currentGameState);
    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');

    const config = currentGameState.game_config || {};

    // Helper to safe string for filename (Allow dots now)
    const safeStr = (str) => (str || '').toString().trim().replace(/[^a-zA-Z0-9\- \.]/g, '').replace(/\s+/g, ' ');

    // Date: DD.MM.YYYY
    let dateRaw = config.date || new Date().toLocaleDateString('pt-BR');
    let dateVal = safeStr(dateRaw.replace(/\//g, '.').replace(/-/g, '.'));

    const venueVal = safeStr(config.venue || document.getElementById('game-venue')?.value || 'padrao');

    // Table: Ensure it looks like "Mesa 1"
    let rawTable = config.table || document.getElementById('game-table')?.value || '1';
    let tableVal = safeStr(rawTable);
    if (!tableVal.toLowerCase().startsWith('mesa')) {
        tableVal = `Mesa ${tableVal}`;
    }

    // Times: Remove colon, e.g. 17:37 -> 1737 (User example style)
    const formatTime = (t) => safeStr(t).replace(':', '').replace('h', '');

    const startVal = formatTime(config.start_time || document.getElementById('start-time')?.value || '00:00');
    // End Time: Use Input value! Fallback to 0000 if empty.
    const endVal = formatTime(config.end_time || document.getElementById('end-time')?.value || '00:00');

    // Format: Resultado_Skat_08.12.2025_Sede_Perzl_Mesa 1_Inicio_1737_Termino_0000.html
    a.download = `Resultado_Skat_${dateVal}_Sede_${venueVal}_${tableVal}_Inicio_${startVal}_Termino_${endVal}.html`;
    a.href = url;
    a.click();
    URL.revokeObjectURL(url);
}

function generateHTMLReport(gameState) {
    // 1. Calculate Finals
    const playerScores = gameState.player_names.map(name => ({ name, score: gameState.scores[name] }));
    playerScores.sort((a, b) => b.score - a.score);
    const winner = playerScores[0];

    // 2. Build History HTML
    let historyRows = '';
    let summaryRows = '';

    // Re-calculate cumulative for table
    const initialScores = {};
    gameState.player_names.forEach(n => initialScores[n] = 0);
    let cumulative = { ...initialScores };

    gameState.game_history.forEach((play, idx) => {
        // --- Summary Table Row ---
        const points = play.result.points;
        const scorer = play.jogador;
        cumulative[scorer] += points;
        if (play.jogo === 'ramsch' && play.houve_empate && play.empates) {
            cumulative[play.empates] += points;
        }

        let cells = `<td>${idx + 1}</td>`;
        gameState.player_names.forEach(name => {
            const score = cumulative[name];
            const scoreClass = score > 0 ? 'positive-score' : (score < 0 ? 'negative-score' : '');
            const style = (name === scorer) ? 'background-color: #FFFF99;' : '';
            const bold = (name === scorer) ? 'font-weight:bold;' : '';
            cells += `<td style="${style} ${bold}" class="${scoreClass}">${score}</td>`;
        });

        let spielSuffix = '';
        if (play.round_mode === 'Bock') spielSuffix = ' B';
        if (play.round_mode === 'Ramsch') spielSuffix = ' R';
        const spielClass = points > 0 ? 'positive-score' : 'negative-score';
        cells += `<td class="bold-text ${spielClass}">${points > 0 ? '+' : ''}${points}${spielSuffix}</td>`;

        summaryRows += `<tr>${cells}</tr>`;

        // --- Details History Block ---
        let details = `Resultado da Última Jogada:<br>Jogador: ${play.jogador}<br>Jogo: ${play.jogo.toUpperCase()}<br>`;
        if (play.com_sem) details += `Com/Sem: ${play.com_sem}<br>`;
        if (play.hand) details += `Hand (+1)<br>`;
        if (play.ouvert) details += `Ouvert (+1)<br>`;
        if (play.schneider) details += `Schneider (+1)<br>`;
        if (play.schwartz) details += `Schwarz (+1)<br>`;
        if (play.kontra) details += `KONTRA!<br>`;
        if (play.reh) details += `REH!<br>`;
        if (play.bock) details += `BOCK!<br>`;
        details += `Pontuação Base: ${play.result.base_score}<br>`;
        details += `Fator Total: ${play.result.total_factor}<br>`;
        details += `Pontos Finais: ${points}<br>`;

        historyRows += `
            <div class='jogada'>
                <div class='jogada-header'>Jogada ${idx + 1}: ${play.jogador} - ${play.jogo.toUpperCase()}</div>
                <div class='detalhe'>${details}</div>
            </div>`;
    });

    // 3. Build Placar HTML
    let placarHtml = '';
    playerScores.forEach(p => {
        const isWinner = p.name === winner.name;
        const colorClass = isWinner ? 'vencedor' : '';
        placarHtml += `<div class='placar-item ${colorClass}'>${p.name}: ${p.score} pontos</div>`;
    });

    // 4. Header Columns for Table
    let tableHeaders = '<th>#</th>';
    gameState.player_names.forEach(name => tableHeaders += `<th>${name}</th>`);
    tableHeaders += '<th>Spiel</th>';

    // 5. Config Details
    const config = gameState.game_config || {};
    // Ensure we handle missing config values gracefully
    const date = config.date || new Date().toLocaleDateString('pt-BR');

    // We try to grab these from the form inputs if missing in gamestate, or just default
    // Ideally user inputs were saved to game_config

    const detailsHtml = `
        <div><strong>Data:</strong> ${date}</div>
        <div><strong>Nome da Mesa:</strong> ${config.table || document.getElementById('game-table')?.value || '-'}</div>
        <div><strong>Sede:</strong> ${config.venue || document.getElementById('game-venue')?.value || '-'}</div>
        <div><strong>Início:</strong> ${config.start_time || document.getElementById('start-time')?.value || '-'}</div>
        <div><strong>Término:</strong> ${config.end_time || new Date().toLocaleTimeString('pt-BR')}</div>
    `;

    return `
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>Relatório da Partida de Räuberskat</title>
            <style>
                body { font-family: sans-serif; margin: 20px; background-color: #f4f4f9; color: #333; }
                h1, h2 { color: #4a4a4a; border-bottom: 2px solid #ddd; padding-bottom: 10px; }
                .container { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                .placar, .pagamentos { margin-bottom: 20px; }
                .placar-item, .pagamento-item { padding: 8px; border-bottom: 1px solid #eee; }
                .vencedor { font-weight: bold; color: #28a745; }
                .jogada { border: 1px solid #ccc; border-radius: 5px; padding: 15px; margin-bottom: 15px; background-color: #fafafa; }
                .jogada-header { font-weight: bold; font-size: 1.1em; margin-bottom: 10px; }
                .detalhe { margin-left: 20px; line-height: 1.4; }
                table.resumo { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                table.resumo th, table.resumo td { border: 1px solid #ddd; padding: 8px; text-align: center; }
                table.resumo th { background-color: #e9e9e9; font-weight: bold; }
                .positive-score { color: green; }
                .negative-score { color: red; }
                .bold-text { font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Relatório da Partida de Räuberskat</h1>
                <h2>Detalhes da Partida</h2>
                <div class='detalhes-partida'>${detailsHtml}</div>
                
                <h2>Placar Final</h2>
                <div class='placar'>${placarHtml}</div>
                
                <h2>Resumo da Partida</h2>
                <table class='resumo'>
                    <thead><tr>${tableHeaders}</tr></thead>
                    <tbody>${summaryRows}</tbody>
                </table>

                <h2>Histórico de Jogadas</h2>
                ${historyRows}
            </div>
        </body>
        </html>`;
}

function populateDropdowns(gameState) {
    const comboJogador = document.getElementById('combo-jogador');
    const comboJogo = document.getElementById('combo-jogo');

    // Players
    comboJogador.innerHTML = '<option value="">Selecione...</option>';
    let activePlayers = [...gameState.player_names];
    if (gameState.num_players === 4) {
        activePlayers.splice(gameState.dealer_index, 1); // Dealer sits out
    }
    activePlayers.forEach(name => {
        comboJogador.add(new Option(name, name));
    });

    // Games
    const bockGames = ["", "ouros", "copas", "espadas", "paus", "null", "grand", "null revolution", "durchmarsch", "ramsch"];
    const ramschGames = ["", "ramsch", "grand hand", "durchmarsch"];
    const list = gameState.current_mode === 'Bock' ? bockGames : ramschGames;

    comboJogo.innerHTML = '';
    list.forEach(g => {
        if (!g) comboJogo.add(new Option('Selecione Jogo...', ''));
        else comboJogo.add(new Option(g.charAt(0).toUpperCase() + g.slice(1), g));
    });
}

// Ramsch Decision Logic (Simulate modal)
async function handleRamschDecision(gameState) {
    if (gameState.awaiting_ramsch_decision && gameState.ramsch_candidates.length > 0) {
        const names = gameState.ramsch_candidates.join(' e ');
        const accept = confirm(`${names}: Deseja nova rodada de Ramsch?`);

        if (accept) {
            // Atomic Group Decision: Send one request for everyone
            await fetch(`${API_URL}/api/game/${currentGameId}/decide_ramsch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jogador: 'todos',
                    deseja_nova_rodada: true,
                    decisao_em_grupo: true
                })
            });
        } else {
            // Reject (just need to send one No to cancel the whole thing)
            await fetch(`${API_URL}/api/game/${currentGameId}/decide_ramsch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jogador: gameState.ramsch_candidates[0], deseja_nova_rodada: false })
            });
        }
        fetchAndRenderGameState(currentGameId); // Refresh after all votes
    }
}
