let socket;
let selectedUser = null;
let jid = null;

function initializeLogin() {
    jid = getUserJid();
    if (jid) {
        setupChat(jid);
    } else {
        alert("Error: JID not found.");
    }
}

function getUserJid() {
    return "user1";
}

function setupChat(jid) {
    socket = io();
    socket.emit("join_room", { jid });

    socket.on("receive_message", data => {
        if (data.recipient === jid || data.sender === jid) {
            addMessage(data.sender, data.message, "left");
            socket.emit("mark_as_read", { recipient: data.sender });
        }
    });

    socket.on("message_status", data => {
        updateMessageStatus(data.sender, data.status);
    });
}

function selectUser(user) {
    selectedUser = user;
    document.getElementById("messages").innerHTML = "";
}

function sendMessage() {
    const message = document.getElementById("message").value;
    if (selectedUser && message.trim() !== "") {
        socket.emit("send_message", { sender: jid, recipient: selectedUser, message });
        addMessage("You", message, "right");
        document.getElementById("message").value = "";
    }
}

function addMessage(sender, message, alignment) {
    const messagesDiv = document.getElementById("messages");
    const msgElement = document.createElement("div");
    msgElement.className = alignment === "right" ? "right-message" : "left-message";
    msgElement.innerHTML = `<strong>${sender}:</strong> ${message} <span class="message-status" id="status-${message}"></span>`;
    messagesDiv.appendChild(msgElement);
}

function updateMessageStatus(sender, status) {
    const messagesDiv = document.getElementById("messages");
    const messageElements = messagesDiv.getElementsByClassName("right-message");
    
    for (let i = 0; i < messageElements.length; i++) {
        const messageElement = messageElements[i];
        if (messageElement.innerHTML.includes(sender)) {
            const statusElement = messageElement.querySelector(".message-status");
            if (status === "sent") {
                statusElement.innerHTML = '✔';
            } else if (status === "delivered") {
                statusElement.innerHTML = '✔✔';
            } else if (status === "read") {
                statusElement.innerHTML = '<span style="color: blue;">✔✔</span>';
            }
        }
    }
}

initializeLogin();
