const chatbot = document.getElementById("chatbot");
const chatButton = document.getElementById("chat-button");
const chatBox = document.getElementById("chat-box");
const closeChat = document.getElementById("close-chat");
const sendButton = document.getElementById("send-button");
const chatInput = document.getElementById("chat-input");
const chatMessages = document.getElementById("chat-messages");

let wasDragging = false;
let isDragging = false;

let startX = 0;
let startY = 0;
let startLeft = 0;
let startTop = 0;


/* OPEN CHAT */
chatButton.addEventListener("click", function () {

    if (wasDragging) {
        wasDragging = false;
        return;
    }

    chatBox.style.display = "block";

    requestAnimationFrame(function () {
        positionChatBox();
        chatInput.focus();
    });
});


/* CLOSE CHAT */
closeChat.addEventListener("click", function () {
    chatBox.style.display = "none";
});


/* FORMAT AI RESPONSE */
function escapeHTML(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}


function formatAIResponse(text) {

    let safeText = escapeHTML(text);

    safeText = safeText.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );

    safeText = safeText.replace(
        /^\s*\*\s+/gm,
        "• "
    );

    safeText = safeText.replace(
        /\n/g,
        "<br>"
    );

    return safeText;
}


/* SEND MESSAGE */
sendButton.addEventListener("click", sendMessage);

chatInput.addEventListener("keydown", function (event) {

    if (event.key === "Enter") {

        event.preventDefault();

        sendMessage();
    }
});


async function sendMessage() {

    const message = chatInput.value.trim();

    if (message === "" || sendButton.disabled) {
        return;
    }


    /* USER MESSAGE */
    const userMessage = document.createElement("p");

    userMessage.className = "user-message";

    userMessage.textContent = message;

    chatMessages.appendChild(userMessage);

    chatMessages.scrollTop = chatMessages.scrollHeight;


    /* CLEAR INPUT */
    chatInput.value = "";


    /* BOT MESSAGE */
    const botMessage = document.createElement("p");

    botMessage.className = "bot-message";

    botMessage.textContent = "Thinking...";

    chatMessages.appendChild(botMessage);

    chatMessages.scrollTop = chatMessages.scrollHeight;


    sendButton.disabled = true;


    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message
            })
        });


        if (!response.ok) {
            throw new Error("Server error");
        }


        const data = await response.text();


        botMessage.innerHTML = formatAIResponse(data);

        chatMessages.scrollTop = chatMessages.scrollHeight;


    } catch (error) {

        console.log(error);

        botMessage.textContent =
            "Sorry, something went wrong. Please try again.";


    } finally {

        sendButton.disabled = false;

        chatInput.focus();
    }
}


/* DRAG CHATBOT */
chatButton.addEventListener("pointerdown", function (event) {

    isDragging = true;

    wasDragging = false;

    startX = event.clientX;
    startY = event.clientY;


    const rect = chatbot.getBoundingClientRect();

    startLeft = rect.left;
    startTop = rect.top;


    chatbot.style.right = "auto";
    chatbot.style.bottom = "auto";

    chatbot.style.left = startLeft + "px";
    chatbot.style.top = startTop + "px";


    chatButton.setPointerCapture(event.pointerId);
});


chatButton.addEventListener("pointermove", function (event) {

    if (!isDragging) {
        return;
    }


    const moveX = event.clientX - startX;
    const moveY = event.clientY - startY;


    const distance = Math.sqrt(
        (moveX * moveX) +
        (moveY * moveY)
    );


    if (distance > 5) {
        wasDragging = true;
    }


    if (!wasDragging) {
        return;
    }


    const buttonWidth = chatButton.offsetWidth;
    const buttonHeight = chatButton.offsetHeight;


    let newLeft = startLeft + moveX;
    let newTop = startTop + moveY;


    const maxLeft =
        window.innerWidth - buttonWidth;

    const maxTop =
        window.innerHeight - buttonHeight;


    newLeft = Math.max(
        0,
        Math.min(newLeft, maxLeft)
    );


    newTop = Math.max(
        0,
        Math.min(newTop, maxTop)
    );


    chatbot.style.left = newLeft + "px";
    chatbot.style.top = newTop + "px";


    if (chatBox.style.display === "block") {
        positionChatBox();
    }
});


chatButton.addEventListener("pointerup", function (event) {

    isDragging = false;

    if (chatButton.hasPointerCapture(event.pointerId)) {
        chatButton.releasePointerCapture(event.pointerId);
    }
});


chatButton.addEventListener("pointercancel", function () {

    isDragging = false;
});


/* CHAT WINDOW POSITION */
function positionChatBox() {

    if (chatBox.style.display !== "block") {
        return;
    }


    const rect = chatbot.getBoundingClientRect();

    const boxWidth = chatBox.offsetWidth;
    const boxHeight = chatBox.offsetHeight;

    const buttonHeight = chatButton.offsetHeight;


    let boxLeft = rect.left;

    let boxTop =
        rect.top -
        boxHeight -
        15;


    /* MOBILE */
    if (window.innerWidth <= 600) {

        boxLeft =
            (window.innerWidth - boxWidth) / 2;

        boxTop =
            (window.innerHeight - boxHeight) / 2;
    }


    /* DESKTOP */
    else {

        if (boxTop < 10) {

            boxTop =
                rect.top +
                buttonHeight +
                15;
        }


        if (
            boxLeft +
            boxWidth >
            window.innerWidth - 10
        ) {

            boxLeft =
                window.innerWidth -
                boxWidth -
                10;
        }


        if (boxLeft < 10) {
            boxLeft = 10;
        }


        if (
            boxTop +
            boxHeight >
            window.innerHeight - 10
        ) {

            boxTop =
                window.innerHeight -
                boxHeight -
                10;
        }


        if (boxTop < 10) {
            boxTop = 10;
        }
    }


    chatBox.style.position = "fixed";

    chatBox.style.left =
        boxLeft + "px";

    chatBox.style.top =
        boxTop + "px";

    chatBox.style.right = "auto";

    chatBox.style.bottom = "auto";
}


/* WINDOW RESIZE */
window.addEventListener("resize", function () {

    if (chatBox.style.display === "block") {
        positionChatBox();
    }
});


/* MOBILE VIEWPORT CHANGE */
if (window.visualViewport) {

    window.visualViewport.addEventListener(
        "resize",
        function () {

            if (chatBox.style.display === "block") {
                positionChatBox();
            }
        }
    );
}