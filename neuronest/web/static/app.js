document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const chatHistory = document.getElementById("chat-history");
    const providerSelect = document.getElementById("model-provider");
    const changeModelBtn = document.getElementById("change-model-btn");
    const modelStatusMsg = document.getElementById("model-status-msg");
    const activeModelName = document.getElementById("active-model-name");

    // Connect to backend API
    async function sendMessage(message) {
        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: message })
            });
            const data = await res.json();
            return data;
        } catch (e) {
            console.error("Error communicating with NeuroNest:", e);
            return { response: "I'm having trouble connecting to my brain right now! 🧠🚫" };
        }
    }

    async function fetchStatus() {
        try {
            const res = await fetch("/api/status");
            const data = await res.json();
            updateDashboard(data);
            if (data.model) {
                updateModelPanel(data.model);
            }
        } catch (e) {
            console.error("Error fetching status:", e);
        }
    }

    async function switchModel(provider) {
        try {
            const res = await fetch("/api/model", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ provider })
            });
            const data = await res.json();
            if (!res.ok) {
                modelStatusMsg.innerText = data.error || "Failed to switch model.";
                modelStatusMsg.classList.add("error");
                return;
            }

            modelStatusMsg.innerText = `Switched to ${data.provider} (${data.model_name}).`;
            modelStatusMsg.classList.remove("error");
            modelStatusMsg.classList.add("success");
            updateModelPanel(data.status || data);
        } catch (e) {
            console.error("Error switching model:", e);
            modelStatusMsg.innerText = "Unable to switch model at this time.";
            modelStatusMsg.classList.add("error");
        }
    }

    function updateModelPanel(modelData) {
        if (!modelData) return;
        providerSelect.value = modelData.provider || "ollama";
        activeModelName.innerText = modelData.model_name || "Unknown";

        if (modelData.ready === false) {
            modelStatusMsg.innerText = modelData.error || "The selected model is unavailable.";
            modelStatusMsg.classList.remove("success");
            modelStatusMsg.classList.add("error");
        } else {
            modelStatusMsg.innerText = `Active provider is ${modelData.provider} (${modelData.model_name}).`;
            modelStatusMsg.classList.remove("error");
            modelStatusMsg.classList.add("success");
        }
    }

    // UI Updates
    function appendMessage(text, isUser = false) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `message ${isUser ? 'msg-user' : 'msg-nn'}`;
        
        const bubble = document.createElement("div");
        bubble.className = "msg-bubble";
        
        // Simple line break parsing for text
        bubble.innerHTML = text.replace(/\n/g, '<br>');
        msgDiv.appendChild(bubble);
        
        const meta = document.createElement("div");
        meta.className = "msg-meta";
        meta.innerText = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        msgDiv.appendChild(meta);

        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function updateDashboard(data) {
        // Name
        if (data.name) document.getElementById("nn-name").innerText = data.name;

        // Evolution stats
        const evo = data.evolution;
        if (evo) {
            document.getElementById("stage-badge").innerText = `Stage ${evo.stage_id}: ${evo.stage_name}`;
            document.getElementById("xp-current").innerText = evo.total_xp;
            document.getElementById("xp-target").innerText = evo.next_stage_xp || 1000;
            document.getElementById("interaction-count").innerText = evo.total_interactions;
            
            // Calculate percentage for XP bar
            const target = evo.next_stage_xp || 1000;
            const percent = Math.min(100, Math.max(0, (evo.total_xp / target) * 100));
            document.getElementById("xp-bar").style.width = `${percent}%`;
        }

        // Memory stats
        const mem = data.memory;
        if (mem) {
            document.getElementById("stat-facts").innerText = mem.total_facts || 0;
            document.getElementById("stat-entities").innerText = mem.total_entities || 0;
            document.getElementById("stat-topics").innerText = mem.total_topics || 0;
            document.getElementById("stat-experiences").innerText = mem.total_experiences || 0;
            document.getElementById("user-name-display").innerText = mem.user_name || "Unknown";
        }

        // Emotion stats
        const emo = data.emotions;
        if (emo) {
            const domKey = emo.dominant_emotion || 'calm';
            document.getElementById("dom-emotion").innerText = domKey.charAt(0).toUpperCase() + domKey.slice(1);
            
            const container = document.getElementById("emotion-bars-container");
            container.innerHTML = ""; // clear old

            for (const [emName, value] of Object.entries(emo.current_state)) {
                // Calculate percentage based on max value (1.0)
                const percent = Math.min(100, Math.max(0, value * 100));
                
                const wrapper = document.createElement("div");
                wrapper.className = "emotion-bar-wrapper";
                
                wrapper.innerHTML = `
                    <div class="emotion-label">
                        <span>${emName.charAt(0).toUpperCase() + emName.slice(1)}</span>
                        <span>${Math.round(percent)}%</span>
                    </div>
                    <div class="bar-bg">
                        <div class="bar-fill bg-${emName}" style="width: ${percent}%"></div>
                    </div>
                `;
                container.appendChild(wrapper);
            }
        }
    }

    changeModelBtn.addEventListener("click", async () => {
        const provider = providerSelect.value;
        await switchModel(provider);
    });

    // Event Listeners
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (!text) return;

        // Display User msg
        appendMessage(text, true);
        userInput.value = "";
        
        // Disable input while waiting
        userInput.disabled = true;
        sendBtn.disabled = true;

        // Send to backend
        const result = await sendMessage(text);
        
        // Display AI response
        if (result.response) {
            appendMessage(result.response, false);
        }

        if (result.llm_status && result.llm_status.ready === false) {
            appendMessage(`⚠️ ${result.llm_status.error || 'The current brain is unavailable.'}`, false);
            modelStatusMsg.innerText = result.llm_status.error || 'The current model is unavailable.';
            modelStatusMsg.classList.remove("success");
            modelStatusMsg.classList.add("error");
        }

        // Check if level up text exists
        if (result.evolution_text) {
            appendMessage(`🌟 **LEVEL UP!** 🌟\n${result.evolution_text}`, false);
        }

        // Re-enable
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();

        // Refresh stats
        fetchStatus();
    });

    // Initial load
    fetchStatus();
});
