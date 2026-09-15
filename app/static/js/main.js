// DecisionAI - Client Controller & Visualizations
let radarChartInstance = null;
let pipelineTimerInterval = null;
let currentReportData = null;

document.addEventListener("DOMContentLoaded", () => {
  initPresets();
  initHoursSlider();
  initFormSubmit();
  initModalsAndDrawers();
  checkEngineStatus();
  fetchHistory();
});

// 1. Quick Presets
function initPresets() {
  document.querySelectorAll(".preset-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.getElementById("inputDilemma").value = btn.dataset.dilemma || "";
      document.getElementById("inputTimeframe").value = btn.dataset.timeframe || "6 months";
      
      const hours = btn.dataset.hours || 15;
      document.getElementById("inputHours").value = hours;
      document.getElementById("hoursLabel").textContent = `${hours} hrs/wk`;

      document.getElementById("inputSkills").value = btn.dataset.skills || "";
      document.getElementById("inputGoal").value = btn.dataset.goal || "Secure an internship / placement";
      
      // Visual feedback
      document.getElementById("inputDilemma").focus();
    });
  });
}

// 2. Weekly Hours Slider
function initHoursSlider() {
  const slider = document.getElementById("inputHours");
  const label = document.getElementById("hoursLabel");
  slider.addEventListener("input", (e) => {
    label.textContent = `${e.target.value} hrs/wk`;
  });
}

// 3. Engine Status & Mode
async function checkEngineStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    const statusText = document.getElementById("engineStatusText");
    if (data.provider === "openai") {
      statusText.textContent = "OpenAI Live API (GPT-4o)";
    } else if (data.provider === "gemini") {
      statusText.textContent = "Gemini Live API";
    } else {
      statusText.textContent = "Offline Simulation Ready";
    }
  } catch (err) {
    console.error("Failed to fetch engine status", err);
  }
}

// 4. Form Submission & Agent Pipeline Animation
function initFormSubmit() {
  const form = document.getElementById("decisionForm");
  const btnSubmit = document.getElementById("btnSimulate");
  const pipelineContainer = document.getElementById("pipelineContainer");
  const resultsContainer = document.getElementById("resultsContainer");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const dilemma = document.getElementById("inputDilemma").value.trim();
    if (!dilemma) return;

    const payload = {
      dilemma: dilemma,
      timeframe: document.getElementById("inputTimeframe").value,
      hours_per_week: parseInt(document.getElementById("inputHours").value, 10),
      current_skills: document.getElementById("inputSkills").value.trim(),
      primary_goal: document.getElementById("inputGoal").value,
      risk_tolerance: "Moderate"
    };

    // UI state: Show pipeline, disable button
    btnSubmit.disabled = true;
    btnSubmit.classList.add("opacity-60", "cursor-not-allowed");
    resultsContainer.classList.add("hidden");
    pipelineContainer.classList.remove("hidden");
    pipelineContainer.scrollIntoView({ behavior: "smooth", block: "start" });

    startPipelineAnimation();

    const startTime = Date.now();
    try {
      const response = await fetch("/api/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      if (!response.ok || !data.success) {
        throw new Error(data.error || "Simulation pipeline failed");
      }

      // Ensure minimum animation duration (2.5s) for realistic multi-agent feel
      const elapsed = Date.now() - startTime;
      const delay = Math.max(0, 2400 - elapsed);
      setTimeout(() => {
        finishPipelineAnimation();
        renderSimulationResults(data.report);
        fetchHistory(); // refresh history drawer
      }, delay);

    } catch (err) {
      alert("Error: " + err.message);
      resetPipeline();
    } finally {
      setTimeout(() => {
        btnSubmit.disabled = false;
        btnSubmit.classList.remove("opacity-60", "cursor-not-allowed");
      }, 2500);
    }
  });
}

// Pipeline Steps Animation Controller
function startPipelineAnimation() {
  const steps = [
    { id: "agentStep1", name: "Situation Analyzer", desc: "Deconstructing constraints..." },
    { id: "agentStep2", name: "Future Simulator", desc: "Simulating parallel futures..." },
    { id: "agentStep3", name: "Decision Critic", desc: "Auditing risks & stress-testing..." },
    { id: "agentStep4", name: "Decision Engine", desc: "Synthesizing scores & verdict..." }
  ];

  steps.forEach((s) => {
    const el = document.getElementById(s.id);
    el.className = "agent-step-card p-4 rounded-xl border border-gray-800 bg-gray-900/60 transition";
    el.querySelector(".step-status").textContent = "Waiting...";
  });

  let seconds = 0;
  const timerLabel = document.getElementById("pipelineTimer");
  timerLabel.textContent = "0s elapsed";
  clearInterval(pipelineTimerInterval);
  pipelineTimerInterval = setInterval(() => {
    seconds++;
    timerLabel.textContent = `${seconds}s elapsed`;
  }, 1000);

  // Animate step 1 immediately
  activateStep("agentStep1", "Analyzing profile & goals...");

  setTimeout(() => {
    completeStep("agentStep1");
    activateStep("agentStep2", "Generating Path A vs B...");
  }, 700);

  setTimeout(() => {
    completeStep("agentStep2");
    activateStep("agentStep3", "Stress-testing assumptions...");
  }, 1400);

  setTimeout(() => {
    completeStep("agentStep3");
    activateStep("agentStep4", "Computing multi-criteria scores...");
  }, 2000);
}

function activateStep(id, text) {
  const el = document.getElementById(id);
  el.classList.add("active");
  el.querySelector(".step-status").textContent = text;
  el.querySelector(".step-status").className = "step-status text-[10px] text-indigo-400 font-medium";
}

function completeStep(id) {
  const el = document.getElementById(id);
  el.classList.remove("active");
  el.classList.add("completed");
  el.querySelector(".step-status").textContent = "Completed";
  el.querySelector(".step-status").className = "step-status text-[10px] text-emerald-400 font-medium";
}

function finishPipelineAnimation() {
  clearInterval(pipelineTimerInterval);
  completeStep("agentStep4");
}

function resetPipeline() {
  clearInterval(pipelineTimerInterval);
  document.getElementById("pipelineContainer").classList.add("hidden");
  const btn = document.getElementById("btnSimulate");
  btn.disabled = false;
  btn.classList.remove("opacity-60", "cursor-not-allowed");
}

// 5. Render Simulation Results & Visualizations
function renderSimulationResults(report) {
  currentReportData = report;
  const container = document.getElementById("resultsContainer");
  const pipeline = document.getElementById("pipelineContainer");

  pipeline.classList.add("hidden");
  container.classList.remove("hidden");
  container.scrollIntoView({ behavior: "smooth", block: "start" });

  const synthesis = report.final_synthesis || {};
  const scores = report.decision_scores || {};
  const sim = report.future_simulation || {};
  const critic = report.decision_critique || {};
  const roadmap = report.action_roadmap || [];

  // Executive Verdict Banner
  document.getElementById("verdictTitle").textContent = `Recommended: ${synthesis.recommended_title || "Path Recommended"}`;
  document.getElementById("verdictSummary").textContent = synthesis.executive_summary || "";
  document.getElementById("verdictConfidenceBadge").textContent = `Confidence: ${synthesis.confidence_score || "85%"}`;
  document.getElementById("counterArgumentText").textContent = synthesis.counter_argument_defense || "";
  document.getElementById("hybridStrategyText").textContent = synthesis.hybrid_strategy || "Combine strengths of both paths sequentially.";

  // Scorecards (Path A vs Path B)
  const scoreA = scores.path_a || {};
  const scoreB = scores.path_b || {};

  document.getElementById("scoreCardTitleA").textContent = scoreA.name || "Path A";
  document.getElementById("scoreCardFitA").textContent = `${scoreA.overall_fit_score || 75}/100 Fit`;
  document.getElementById("scoreDiffA").textContent = `${scoreA.difficulty || 8}/10`;
  document.getElementById("barDiffA").style.width = `${(scoreA.difficulty || 8) * 10}%`;
  document.getElementById("scoreTimeA").textContent = `${scoreA.time_required_months || 6} Months`;
  document.getElementById("barTimeA").style.width = `${Math.min(100, (scoreA.time_required_months || 6) * 16.6)}%`;
  document.getElementById("scoreGrowthA").textContent = `${scoreA.skill_growth || 9}/10`;
  document.getElementById("barGrowthA").style.width = `${(scoreA.skill_growth || 9) * 10}%`;
  document.getElementById("scoreFeasA").textContent = `${scoreA.feasibility_score || 70}/100`;
  document.getElementById("barFeasA").style.width = `${scoreA.feasibility_score || 70}%`;

  document.getElementById("scoreCardTitleB").textContent = scoreB.name || "Path B";
  document.getElementById("scoreCardFitB").textContent = `${scoreB.overall_fit_score || 85}/100 Fit`;
  document.getElementById("scoreDiffB").textContent = `${scoreB.difficulty || 6}/10`;
  document.getElementById("barDiffB").style.width = `${(scoreB.difficulty || 6) * 10}%`;
  document.getElementById("scoreTimeB").textContent = `${scoreB.time_required_months || 4} Months`;
  document.getElementById("barTimeB").style.width = `${Math.min(100, (scoreB.time_required_months || 4) * 16.6)}%`;
  document.getElementById("scoreGrowthB").textContent = `${scoreB.skill_growth || 8}/10`;
  document.getElementById("barGrowthB").style.width = `${(scoreB.skill_growth || 8) * 10}%`;
  document.getElementById("scoreFeasB").textContent = `${scoreB.feasibility_score || 85}/100`;
  document.getElementById("barFeasB").style.width = `${scoreB.feasibility_score || 85}%`;

  // Render Radar Chart
  renderRadarChart(scores);

  // Future Simulator: Path A Details
  const pathA = sim.path_a || {};
  document.getElementById("pathATitle").textContent = pathA.title || "Path A";
  document.getElementById("pathATagline").textContent = pathA.tagline || "";
  document.getElementById("pathAEffort").textContent = `${pathA.weekly_effort_hours || 18} hrs/week`;
  document.getElementById("pathANarrative").textContent = pathA.narrative || "";
  document.getElementById("pathAReadiness").textContent = pathA.internship_readiness || "Moderate";
  document.getElementById("pathATimeline").textContent = `${pathA.timeline_to_readiness_months || 6} Months`;

  const skillsListA = document.getElementById("pathASkills");
  skillsListA.innerHTML = "";
  (pathA.skills_to_learn || []).forEach((s) => {
    skillsListA.innerHTML += `<li class="flex items-center"><i class="fa-solid fa-check text-purple-400 mr-1.5 text-[10px]"></i><span>${s}</span></li>`;
  });

  const projA = document.getElementById("pathAProjects");
  projA.innerHTML = "";
  (pathA.milestone_projects || []).forEach((p) => {
    projA.innerHTML += `
      <div class="p-2.5 rounded-lg bg-gray-900/80 border border-gray-800">
        <div class="font-semibold text-white text-xs">${p.name}</div>
        <div class="text-[11px] text-gray-400 mt-0.5">${p.description}</div>
      </div>`;
  });

  const diffA = document.getElementById("pathADifficulties");
  diffA.innerHTML = "";
  (pathA.expected_difficulties || []).forEach((d) => {
    diffA.innerHTML += `<li>${d}</li>`;
  });

  // Future Simulator: Path B Details
  const pathB = sim.path_b || {};
  document.getElementById("pathBTitle").textContent = pathB.title || "Path B";
  document.getElementById("pathBTagline").textContent = pathB.tagline || "";
  document.getElementById("pathBEffort").textContent = `${pathB.weekly_effort_hours || 14} hrs/week`;
  document.getElementById("pathBNarrative").textContent = pathB.narrative || "";
  document.getElementById("pathBReadiness").textContent = pathB.internship_readiness || "Very High";
  document.getElementById("pathBTimeline").textContent = `${pathB.timeline_to_readiness_months || 4} Months`;

  const skillsListB = document.getElementById("pathBSkills");
  skillsListB.innerHTML = "";
  (pathB.skills_to_learn || []).forEach((s) => {
    skillsListB.innerHTML += `<li class="flex items-center"><i class="fa-solid fa-check text-cyan-400 mr-1.5 text-[10px]"></i><span>${s}</span></li>`;
  });

  const projB = document.getElementById("pathBProjects");
  projB.innerHTML = "";
  (pathB.milestone_projects || []).forEach((p) => {
    projB.innerHTML += `
      <div class="p-2.5 rounded-lg bg-gray-900/80 border border-gray-800">
        <div class="font-semibold text-white text-xs">${p.name}</div>
        <div class="text-[11px] text-gray-400 mt-0.5">${p.description}</div>
      </div>`;
  });

  const diffB = document.getElementById("pathBDifficulties");
  diffB.innerHTML = "";
  (pathB.expected_difficulties || []).forEach((d) => {
    diffB.innerHTML += `<li>${d}</li>`;
  });

  // Decision Critic: Adversarial Stress Test
  const critA = critic.path_a_critique || {};
  const critB = critic.path_b_critique || {};

  document.getElementById("criticTitleA").textContent = `Critique: ${pathA.title || "Path A"}`;
  document.getElementById("criticBurnoutA").textContent = `Burnout Risk: ${critA.burnout_risk_score || 8}/10`;
  document.getElementById("criticMarketA").textContent = critA.market_reality_check || "";
  document.getElementById("criticMitigationA").textContent = critA.mitigation_strategy || "";

  const spotsA = document.getElementById("criticBlindSpotsA");
  spotsA.innerHTML = "";
  (critA.blind_spots || []).forEach((b) => {
    spotsA.innerHTML += `<li>${b}</li>`;
  });

  document.getElementById("criticTitleB").textContent = `Critique: ${pathB.title || "Path B"}`;
  document.getElementById("criticBurnoutB").textContent = `Burnout Risk: ${critB.burnout_risk_score || 5}/10`;
  document.getElementById("criticMarketB").textContent = critB.market_reality_check || "";
  document.getElementById("criticMitigationB").textContent = critB.mitigation_strategy || "";

  const spotsB = document.getElementById("criticBlindSpotsB");
  spotsB.innerHTML = "";
  (critB.blind_spots || []).forEach((b) => {
    spotsB.innerHTML += `<li>${b}</li>`;
  });

  document.getElementById("criticTradeoffVerdict").textContent = critic.critical_tradeoff_verdict || "";

  // 6-Month Action Roadmap
  const timelineEl = document.getElementById("roadmapTimeline");
  timelineEl.innerHTML = "";
  roadmap.forEach((step, idx) => {
    timelineEl.innerHTML += `
      <div class="flex items-start space-x-4 p-4 rounded-xl bg-gray-900/60 border border-gray-800">
        <div class="w-16 shrink-0 text-center font-mono font-bold text-xs px-2.5 py-1.5 rounded-lg bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
          ${step.phase}
        </div>
        <div class="space-y-1 text-xs">
          <div class="font-bold text-white text-sm">${step.milestone}</div>
          <div class="text-gray-300"><strong class="text-gray-400">Focus:</strong> ${step.focus}</div>
          <div class="text-emerald-400/90"><strong class="text-emerald-500">Key Deliverable:</strong> ${step.deliverable}</div>
        </div>
      </div>`;
  });
}

// 6. Chart.js Radar Visualization
function renderRadarChart(scores) {
  const ctx = document.getElementById("radarChart").getContext("2d");

  if (radarChartInstance) {
    radarChartInstance.destroy();
  }

  const dimensions = scores.radar_dimensions || [
    "Feasibility", "Market Demand", "Skill Growth", "Portfolio Impact", "Speed"
  ];
  const seriesA = scores.radar_series_a || [6, 8, 9, 8, 3];
  const seriesB = scores.radar_series_b || [9, 9, 8, 9, 7];

  radarChartInstance = new Chart(ctx, {
    type: "radar",
    data: {
      labels: dimensions,
      datasets: [
        {
          label: scores.path_a?.name || "Path A",
          data: seriesA,
          backgroundColor: "rgba(168, 85, 247, 0.25)",
          borderColor: "rgba(168, 85, 247, 0.9)",
          pointBackgroundColor: "#a855f7",
          pointBorderColor: "#fff",
          borderWidth: 2
        },
        {
          label: scores.path_b?.name || "Path B",
          data: seriesB,
          backgroundColor: "rgba(6, 182, 212, 0.25)",
          borderColor: "rgba(6, 182, 212, 0.9)",
          pointBackgroundColor: "#06b6d4",
          pointBorderColor: "#fff",
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          min: 0,
          max: 10,
          ticks: {
            stepSize: 2,
            display: false
          },
          grid: {
            color: "rgba(75, 85, 99, 0.3)"
          },
          angleLines: {
            color: "rgba(75, 85, 99, 0.3)"
          },
          pointLabels: {
            color: "#9ca3af",
            font: {
              size: 11,
              family: "'Inter', sans-serif"
            }
          }
        }
      },
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            color: "#d1d5db",
            boxWidth: 12,
            font: { size: 12 }
          }
        }
      }
    }
  });
}

// 7. Modals, History, Copy & Print Handlers
function initModalsAndDrawers() {
  // History Drawer toggles
  const drawer = document.getElementById("historyDrawer");
  document.getElementById("btnOpenHistory").addEventListener("click", () => {
    drawer.classList.remove("hidden");
    fetchHistory();
  });
  document.getElementById("btnCloseHistory").addEventListener("click", () => {
    drawer.classList.add("hidden");
  });

  // Settings Modal toggles
  const modal = document.getElementById("configModal");
  document.getElementById("btnOpenConfig").addEventListener("click", () => {
    modal.classList.remove("hidden");
  });
  document.getElementById("btnCloseConfig").addEventListener("click", () => {
    modal.classList.add("hidden");
  });

  // Save Settings
  document.getElementById("btnSaveConfig").addEventListener("click", async () => {
    const openaiKey = document.getElementById("inputOpenAiKey")?.value.trim() || "";
    const geminiKey = document.getElementById("inputApiKey")?.value.trim() || "";
    try {
      const res = await fetch("/api/configure_key", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ openai_key: openaiKey, gemini_key: geminiKey })
      });
      const data = await res.json();
      if (data.success) {
        modal.classList.add("hidden");
        checkEngineStatus();
        alert(`Settings updated! Active Mode: ${data.mode}`);
      }
    } catch (e) {
      alert("Error saving settings: " + e.message);
    }
  });

  // Print Report
  document.getElementById("btnPrintReport").addEventListener("click", () => {
    window.print();
  });

  // Copy Summary
  document.getElementById("btnCopyReport").addEventListener("click", () => {
    if (!currentReportData) return;
    const syn = currentReportData.final_synthesis || {};
    const text = `DecisionAI Recommendation Report:\n\n${syn.recommended_title}\n\nVerdict: ${syn.executive_summary}\n\nHybrid Strategy: ${syn.hybrid_strategy}`;
    navigator.clipboard.writeText(text).then(() => {
      alert("Decision summary copied to clipboard!");
    });
  });
}

// 8. History Drawer Data Loading
async function fetchHistory() {
  try {
    const res = await fetch("/api/history");
    const data = await res.json();
    if (!data.success) return;

    const listEl = document.getElementById("historyList");
    const badge = document.getElementById("historyBadge");
    const sims = data.simulations || [];

    badge.textContent = sims.length;

    if (sims.length === 0) {
      listEl.innerHTML = `<p class="text-xs text-gray-500 text-center py-8">No saved simulations yet.</p>`;
      return;
    }

    listEl.innerHTML = "";
    sims.forEach((item) => {
      const card = document.createElement("div");
      card.className = "p-3 rounded-xl bg-gray-900 border border-gray-800 hover:border-indigo-500/50 cursor-pointer transition space-y-1.5";
      card.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="text-[10px] font-mono text-indigo-400 uppercase font-semibold">${item.timeframe || "6 months"}</span>
          <button class="btn-del text-gray-500 hover:text-red-400 text-xs p-1" data-id="${item.id}" title="Delete">
            <i class="fa-regular fa-trash-can"></i>
          </button>
        </div>
        <div class="text-xs font-semibold text-white line-clamp-2">${item.dilemma}</div>
        <div class="text-[11px] text-emerald-400 flex items-center justify-between">
          <span>${item.recommended_title || "Recommended"}</span>
          <span class="text-gray-500 text-[10px]">${item.confidence_score || ""}</span>
        </div>
      `;

      card.addEventListener("click", (e) => {
        if (e.target.closest(".btn-del")) return;
        loadHistoryItem(item.id);
      });

      card.querySelector(".btn-del").addEventListener("click", async (e) => {
        e.stopPropagation();
        if (confirm("Delete this saved simulation?")) {
          await deleteHistoryItem(item.id);
        }
      });

      listEl.appendChild(card);
    });
  } catch (err) {
    console.error("Failed to load history:", err);
  }
}

async function loadHistoryItem(id) {
  try {
    const res = await fetch(`/api/history/${id}`);
    const data = await res.json();
    if (data.success && data.simulation && data.simulation.report) {
      document.getElementById("historyDrawer").classList.add("hidden");
      renderSimulationResults(data.simulation.report);
    }
  } catch (e) {
    alert("Error loading simulation: " + e.message);
  }
}

async function deleteHistoryItem(id) {
  try {
    await fetch(`/api/history/${id}`, { method: "DELETE" });
    fetchHistory();
  } catch (e) {
    console.error("Error deleting history item", e);
  }
}

