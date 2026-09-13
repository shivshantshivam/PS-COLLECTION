const chatbot = document.getElementById("chatbot");

const chatButton = document.getElementById("chat-button");
const chatBox = document.getElementById("chat-box");
const closeChat = document.getElementById("close-chat");

const sendButton = document.getElementById("send-button");
const chatInput = document.getElementById("chat-input");
const chatMessages = document.getElementById("chat-messages");


/* =========================
   OPEN / CLOSE CHAT
========================= */

let wasDragging = false;

chatButton.addEventListener("click", function () {

    if (wasDragging) {
        wasDragging = false;
        return;
    }

    chatBox.style.display = "block";

    positionChatBox();

});


closeChat.addEventListener("click", function () {

    chatBox.style.display = "none";

});


/* =========================
   SEND MESSAGE
========================= */

sendButton.addEventListener("click", sendMessage);


chatInput.addEventListener("keypress", function (event) {

    if (event.key === "Enter") {
        sendMessage();
    }

});


/* =========================
   FORMAT AI RESPONSE
========================= */

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


/* =========================
   SEND MESSAGE
========================= */

function sendMessage() {

    const message = chatInput.value.trim();

    if (message === "") {
        return;
    }


    const userMessage =
        document.createElement("p");

    userMessage.className =
        "user-message";

    userMessage.textContent =
        message;

    chatMessages.appendChild(
        userMessage
    );


    chatMessages.scrollTop =
        chatMessages.scrollHeight;


    chatInput.value = "";


    const botMessage =
        document.createElement("p");

    botMessage.className =
        "bot-message";

    botMessage.textContent =
        "Thinking...";

    chatMessages.appendChild(
        botMessage
    );


    chatMessages.scrollTop =
        chatMessages.scrollHeight;


    sendButton.disabled = true;


    fetch("/chat", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            message: message
        })

    })

    .then(response => {

        if (!response.ok) {
            throw new Error("Server error");
        }

        return response.text();

    })

    .then(data => {

        botMessage.innerHTML =
            formatAIResponse(data);

        chatMessages.scrollTop =
            chatMessages.scrollHeight;

    })

    .catch(error => {

        botMessage.textContent =
            "Sorry, something went wrong. Please try again.";

        console.log(error);

    })

    .finally(() => {

        sendButton.disabled = false;

        chatInput.focus();

    });

}


/* =========================
   DRAG CHATBOT
========================= */

let isDragging = false;

let startX = 0;
let startY = 0;

let startLeft = 0;
let startTop = 0;

let movedDistance = 0;


chatButton.addEventListener(
    "pointerdown",
    function (event) {

        isDragging = true;

        wasDragging = false;

        movedDistance = 0;

        startX = event.clientX;
        startY = event.clientY;


        const rect =
            chatbot.getBoundingClientRect();


        startLeft = rect.left;
        startTop = rect.top;


        chatbot.style.right = "auto";
        chatbot.style.bottom = "auto";

        chatbot.style.left =
            startLeft + "px";

        chatbot.style.top =
            startTop + "px";


        chatButton.setPointerCapture(
            event.pointerId
        );

    }
);


chatButton.addEventListener(
    "pointermove",
    function (event) {

        if (!isDragging) {
            return;
        }


        const moveX =
            event.clientX - startX;

        const moveY =
            event.clientY - startY;


        movedDistance =
            Math.sqrt(
                (moveX * moveX) +
                (moveY * moveY)
            );


        if (movedDistance > 5) {
            wasDragging = true;
        }


        if (!wasDragging) {
            return;
        }


        let newLeft =
            startLeft + moveX;

        let newTop =
            startTop + moveY;


        /*
           Keep chatbot button
           inside the screen
        */

        const buttonWidth =
            chatButton.offsetWidth;

        const buttonHeight =
            chatButton.offsetHeight;


        const maxLeft =
            window.innerWidth -
            buttonWidth;

        const maxTop =
            window.innerHeight -
            buttonHeight;


        newLeft =
            Math.max(
                0,
                Math.min(
                    newLeft,
                    maxLeft
                )
            );


        newTop =
            Math.max(
                0,
                Math.min(
                    newTop,
                    maxTop
                )
            );


        chatbot.style.left =
            newLeft + "px";

        chatbot.style.top =
            newTop + "px";


        /*
           Automatically position
           chat window near button
        */

        positionChatBox();

    }
);


chatButton.addEventListener(
    "pointerup",
    function (event) {

        isDragging = false;

        if (
            chatButton.hasPointerCapture(
                event.pointerId
            )
        ) {

            chatButton.releasePointerCapture(
                event.pointerId
            );

        }

    }
);


chatButton.addEventListener(
    "pointercancel",
    function () {

        isDragging = false;

    }
);


/* =========================
   CHAT WINDOW POSITION
========================= */

function positionChatBox() {

    const rect =
        chatbot.getBoundingClientRect();

    const boxWidth =
        chatBox.offsetWidth;

    const boxHeight =
        chatBox.offsetHeight;

    const buttonWidth =
        chatButton.offsetWidth;

    const buttonHeight =
        chatButton.offsetHeight;


    let boxLeft =
        rect.left;

    let boxTop =
        rect.top -
        boxHeight -
        15;


    /*
       If there is not enough
       space above, put chat below
    */

    if (boxTop < 10) {

        boxTop =
            rect.top +
            buttonHeight +
            15;

    }


    /*
       Keep inside left/right
    */

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


    /*
       Keep inside top/bottom
    */

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


    chatBox.style.position =
        "fixed";

    chatBox.style.left =
        boxLeft + "px";

    chatBox.style.top =
        boxTop + "px";

    chatBox.style.right =
        "auto";

    chatBox.style.bottom =
        "auto";

}


/* =========================
   WINDOW RESIZE
========================= */

window.addEventListener(
    "resize",
    function () {

        if (
            chatBox.style.display === "block"
        ) {

            positionChatBox();

        }

    }
);