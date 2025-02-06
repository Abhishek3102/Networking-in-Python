let socket;
let room = "general";
let isTyping = false;
let typingTimeout;

function setupChat(username) {
  socket = io();
  socket.emit("join_room", { username: username, room: room });

  socket.on("user_joined", (data) => {
    const messages = document.getElementById("messages");
    messages.innerHTML += `<div class="notification">${data.username} joined the room.</div>`;
  });

  socket.on("user_left", (data) => {
    const messages = document.getElementById("messages");
    messages.innerHTML += `<div class="notification">${data.username} left the room.</div>`;
  });

  socket.on("update_user_list", (data) => {
    const userList = document.getElementById("user-list");
    userList.innerHTML = data.users.map((user) => `<li>${user}</li>`).join("");
  });

  socket.on("receive_message", (data) => {
    const messages = document.getElementById("messages");
    const messageClass =
      data.username === username ? "right-message" : "left-message";
    messages.innerHTML += `<div class="message ${messageClass}">${data.message}</div>`;
    messages.scrollTop = messages.scrollHeight;
  });

  socket.on("receive_file", (data) => {
    const messages = document.getElementById("messages");
    const messageClass =
      data.username === username ? "right-message" : "left-message";
    messages.innerHTML += `<div class="message ${messageClass}"><a href="${data.file_url}" download>${data.filename}</a></div>`;
    messages.scrollTop = messages.scrollHeight;
  });

  socket.on("typing", (data) => {
    const typingIndicator = document.getElementById("typing-indicator");
    if (data.isTyping) {
      typingIndicator.innerHTML = `${data.username} is typing...`;
    } else {
      typingIndicator.innerHTML = "";
    }
  });

  document.getElementById("message").addEventListener("input", () => {
    if (!isTyping) {
      isTyping = true;
      socket.emit("typing", { username: username, room: room, isTyping: true });
    }
    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => {
      isTyping = false;
      socket.emit("typing", {
        username: username,
        room: room,
        isTyping: false,
      });
    }, 1000);
  });
}

function sendMessage() {
  const message = document.getElementById("message").value;
  if (message) {
    socket.emit("send_message", {
      username: username,
      room: room,
      message: message,
    });
    document.getElementById("message").value = "";
  }
}

function sendFile() {
  const fileInput = document.getElementById("file-input");
  fileInput.click();
  fileInput.onchange = function () {
    const file = fileInput.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        const fileData = e.target.result.split(",")[1];
        socket.emit("send_file", {
          username: username,
          room: room,
          filename: file.name,
          file_data: fileData,
        });
      };
      reader.readAsDataURL(file);
    }
  };
}
