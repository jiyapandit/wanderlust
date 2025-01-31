document.addEventListener("DOMContentLoaded", loadChatHistory);

document.getElementById("send-btn").addEventListener("click", sendMessage);
document.getElementById("voice-btn").addEventListener("click", startVoiceInput);
document.getElementById("stop-voice-btn").addEventListener("click", stopVoice);

let speechSynthesisInstance = null;

function sendMessage() {
    let userInput = document.getElementById("user-input").value.trim();
    if (!userInput) return;

    appendMessage("user", userInput);
    saveMessage("user", userInput);
    fetchResponse(userInput);
    document.getElementById("user-input").value = "";
}

function sendQuickMessage(message) {
    appendMessage("user", message);
    saveMessage("user", message);
    fetchResponse(message);
}

function fetchResponse(userMessage) {
    fetch('/ask', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage })
    })
    .then(response => response.json())
    .then(data => {
        appendMessage("bot", data.response);
        saveMessage("bot", data.response);
        speakResponse(data.response);
    });
}

function appendMessage(sender, message) {
    let chatArea = document.getElementById("chat-area");
    let div = document.createElement("div");
    div.className = sender === "user" ? "user-message" : "bot-message";
    div.innerHTML = `<strong>${sender === "user" ? "You" : "Bot"}:</strong> ${message}`;
    chatArea.appendChild(div);
    chatArea.scrollTop = chatArea.scrollHeight;
}

function startVoiceInput() {
    let recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.start();
    recognition.onresult = function(event) {
        let voiceText = event.results[0][0].transcript;
        document.getElementById("user-input").value = voiceText;
        sendMessage();
    };
}

function speakResponse(text) {
    speechSynthesisInstance = new SpeechSynthesisUtterance(text);
    speechSynthesis.speak(speechSynthesisInstance);
    document.getElementById("stop-voice-btn").classList.remove("hidden");
}

function stopVoice() {
    if (speechSynthesisInstance) {
        speechSynthesis.cancel();
        document.getElementById("stop-voice-btn").classList.add("hidden");
    }
}
