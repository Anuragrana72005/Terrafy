const sendBtn = document.getElementById("sendBtn");
const questionInput = document.getElementById("question");
const chatBox = document.getElementById("chatBox");
const languageSelect = document.getElementById("language");
const stopBtn = document.getElementById("stopBtn");
const avatar = document.getElementById("avatar");

let currentAudio = null;

// Send button
sendBtn.addEventListener("click", sendMessage);

// Enter key
questionInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});

// Stop button logic
if (stopBtn) {
    stopBtn.addEventListener("click", function () {
        if (currentAudio) {
            currentAudio.pause();
            currentAudio.currentTime = 0;
            if (avatar) avatar.classList.remove("speaking");
        }
    });
}

// Function for quick suggestion chips
function setPrompt(text) {
    questionInput.value = text;
    sendMessage();
}

function sendMessage() {
    const question = questionInput.value.trim();
    if (!question) return;

    // Stop current audio and animation if user asks a new question
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        if (avatar) avatar.classList.remove("speaking");
    }

    // Append User Message
    const userMsg = document.createElement("div");
    userMsg.className = "msg user";
    userMsg.innerHTML = `<div class="msg-content">${question}</div>`;
    chatBox.appendChild(userMsg);

    questionInput.value = "";

    // Append Loading Message
    const loadingMsg = document.createElement("div");
    loadingMsg.className = "msg bot";
    loadingMsg.innerHTML = `<div class="msg-content typing-indicator">⏳ Processing signal...</div>`;
    chatBox.appendChild(loadingMsg);

    chatBox.scrollTop = chatBox.scrollHeight;

    // API Call - Explicitly point to localhost:5000 if not running from the same origin
    // If Flask is serving this HTML, "/ask" works. If using Live Server, use "http://127.0.0.1:5000/ask"
    fetch("/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            question: question,
            language: languageSelect ? languageSelect.value : "English"
        })
    })
    .then(async (res) => {
        if (!res.ok) {
            // Catch server errors (500) and pass to catch block
            throw new Error(`Server responded with status: ${res.status}`);
        }
        return res.json();
    })
    .then(data => {
        chatBox.removeChild(loadingMsg);

        // Clean formatting
        let cleanText = data.answer
            .replace(/\*\*/g, "")
            .replace(/\*/g, "")
            .replace(/__/g, "")
            .replace(/`/g, "");

        // Append Bot Response
        const botMsg = document.createElement("div");
        botMsg.className = "msg bot";
        botMsg.innerHTML = `<div class="msg-content">${cleanText}</div>`;
        chatBox.appendChild(botMsg);
        chatBox.scrollTop = chatBox.scrollHeight;

        // Play natural AI voice AND trigger animation
        if (data.audio) {
            currentAudio = new Audio("data:audio/mp3;base64," + data.audio);
            
            // Start Avatar animation
            if (avatar) avatar.classList.add("speaking");
            currentAudio.play();

            // Stop Avatar animation when audio finishes naturally
            currentAudio.onended = function() {
                if (avatar) avatar.classList.remove("speaking");
            };
        }
    })
    .catch(err => {
        chatBox.removeChild(loadingMsg);

        const errorMsg = document.createElement("div");
        errorMsg.className = "msg bot";
        errorMsg.innerHTML = `<div class="msg-content" style="color:#ff5252;">❌ Connection lost or server error. Please try again.</div>`;
        chatBox.appendChild(errorMsg);
        console.error("Fetch error:", err);
        
        if (avatar) avatar.classList.remove("speaking"); // Failsafe
    });
}