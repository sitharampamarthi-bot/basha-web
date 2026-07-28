document.addEventListener("DOMContentLoaded", function () {

    const openButton =
        document.getElementById("bashaAiOpenButton");

    const shell =
        document.getElementById("bashaAiShell");

    if (!openButton || !shell) {
        return;
    }

    const backdrop =
        document.getElementById("bashaAiBackdrop");

    const closeButton =
        document.getElementById("bashaAiCloseButton");

    const clearButton =
        document.getElementById("bashaAiClearButton");

    const voiceToggle =
        document.getElementById("bashaAiVoiceToggle");

    const character =
        document.getElementById("bashaAiCharacter");

    const assistantImage =
        "/static/images/basha-ai-assistant.png";

    const idleImage =
        "/static/images/basha-ai-idle.webp";

    const speakingImage =
        "/static/images/basha-ai-speaking.webp";    

    const characterSection =
        document.getElementById(
            "bashaAiCharacterSection"
        );

    const introBubble =
        document.getElementById("bashaAiIntroBubble");

    const messages =
        document.getElementById("bashaAiMessages");

    const thinking =
        document.getElementById("bashaAiThinking");

    const errorBox =
        document.getElementById("bashaAiError");

    const input =
        document.getElementById("bashaAiInput");

    const micButton =
        document.getElementById("bashaAiMicButton");

    const sendButton =
        document.getElementById("bashaAiSendButton");

    const status =
        document.getElementById("bashaAiStatus");

    const voiceStatus =
        document.getElementById("bashaAiVoiceStatus");

    const characterCount =
        document.getElementById(
            "bashaAiCharacterCount"
        );


    let initialized = false;
    let isSending = false;
    let voiceReplyEnabled = true;
    let recognition = null;
    let isListening = false;
    let userLanguageCode = "en";
    let conversationHistory = [];


    const speechLanguageMap = {
        en: "en-IN",
        te: "te-IN",
        hi: "hi-IN",
        ta: "ta-IN",
        kn: "kn-IN",
        ml: "ml-IN",
        mr: "mr-IN",
        gu: "gu-IN",
        bn: "bn-IN",
        pa: "pa-IN",
        ur: "ur-IN",
        or: "or-IN",
        as: "as-IN",
        ne: "ne-NP"
    };


    function escapeHtml(value) {
        return String(value || "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }


    function getCurrentTime() {
        return new Intl.DateTimeFormat(
            [],
            {
                hour: "2-digit",
                minute: "2-digit"
            }
        ).format(new Date());
    }


    function showError(message) {
        errorBox.textContent =
            message || "Something went wrong.";

        errorBox.hidden = false;
    }


    function hideError() {
        errorBox.hidden = true;
        errorBox.textContent = "";
    }


    function scrollMessagesToBottom() {
        requestAnimationFrame(function () {
            messages.scrollTop =
                messages.scrollHeight;
        });
    }


    function resizeInput() {
        input.style.height = "auto";

        input.style.height =
            Math.min(
                input.scrollHeight,
                130
            ) + "px";
    }


    function updateCharacterCount() {
        characterCount.textContent =
            `${input.value.length} / 5000`;

        sendButton.disabled =
            isSending ||
            !input.value.trim();
    }


    function addMessage(role, text) {
        const row =
            document.createElement("div");

        row.className =
            "basha-ai-message-row " +
            (
                role === "user"
                    ? "is-user"
                    : "is-assistant"
            );

        row.innerHTML = `
            <div class="basha-ai-message">
                ${escapeHtml(text)}
                <span class="basha-ai-message-time">
                    ${getCurrentTime()}
                </span>
            </div>
        `;

        messages.appendChild(row);

        conversationHistory.push({
            role: role,
            text: text
        });

        if (conversationHistory.length > 20) {
            conversationHistory =
                conversationHistory.slice(-20);
        }

        scrollMessagesToBottom();
    }


    function speakText(text) {
        if (
            !voiceReplyEnabled ||
            !("speechSynthesis" in window) ||
            !text
        ) {
            return;
        }

        window.speechSynthesis.cancel();

        const utterance =
            new SpeechSynthesisUtterance(text);

        utterance.lang =
            speechLanguageMap[userLanguageCode]
            || "en-IN";

        utterance.rate = 0.88;
        utterance.pitch = 1;
        utterance.volume = 1;

        const availableVoices =
            window.speechSynthesis.getVoices();

        utterance.voice =
            availableVoices.find(function (voice) {
                return voice.lang === utterance.lang;
            })
            ||
            availableVoices.find(function (voice) {
                return voice.lang
                    .toLowerCase()
                    .startsWith(
                        userLanguageCode.toLowerCase()
                    );
            })
            ||
            null;

        utterance.onstart = function () {
            character.classList.add(
                "is-speaking"
            );
            character.src =
                speakingImage;

            status.textContent =
                "Speaking...";
        };

        utterance.onend = function () {
            character.classList.remove(
                "is-speaking"
            );
            character.src =
                idleImage;

            status.textContent =
                "Online";
        };

        utterance.onerror = function () {
            character.classList.remove(
                "is-speaking"
            );
            character.src =
                idleImage;

            status.textContent =
                "Online";
        };

        window.speechSynthesis.speak(
            utterance
        );
    }

    async function typeGreeting(text){

        introBubble.textContent = "";

        for(const letter of text){

            introBubble.textContent += letter;

            await new Promise(function(resolve){

                setTimeout(resolve,18);

            });

        }

    }


    async function loadGreeting(){

        introBubble.innerHTML = `
            <span class="basha-ai-intro-loading">
                <span></span>
                <span></span>
                <span></span>
            </span>
        `;

        try{

            const response = await fetch(
                "/api/ai-assistant/greeting"
            );

            const data =
                await response.json();

            if(!response.ok || !data.success){

                throw new Error(
                    data.error
                );

            }

            userLanguageCode =
                data.languageCode || "en";

            introBubble.classList.add(
                "show"
            );    

            await typeGreeting(
                data.greeting
            );

            setupSpeechRecognition();

            setTimeout(function(){

                speakText(
                    data.greeting
                );

            },300);

        }
        catch(error){

            introBubble.textContent =
                "Hi 👋 I am Basha AI Assistant.";

            showError(
                error.message
            );

        }

    }


    function openAssistant() {
        shell.hidden = false;

        document.body.style.overflow =
            "hidden";

        hideError();

        character.src =
            idleImage;

        character.classList.remove(
            "basha-ai-fly"
        );

        void character.offsetWidth;

        character.classList.add(
            "basha-ai-fly"
        );

        introBubble.classList.remove(
            "show"
        );

        setTimeout(function () {
            introBubble.classList.add(
                "show"
            );
        }, 500);

        setTimeout(function () {
            input.focus();
        }, 1100);

        if (!initialized) {
            initialized = true;

            setTimeout(function () {
                loadGreeting();
            }, 600);
        }
    }


    function closeAssistant() {
        shell.hidden = true;

        document.body.style.overflow = "";

        if (
            "speechSynthesis" in window
        ) {
            window.speechSynthesis.cancel();
        }

        stopListening();
    }


    function clearConversation() {
        conversationHistory = [];
        messages.innerHTML = "";
        input.value = "";

        resizeInput();
        updateCharacterCount();
        hideError();

        if (
            "speechSynthesis" in window
        ) {
            window.speechSynthesis.cancel();
        }

        loadGreeting();
    }


    async function sendMessage() {
        const message =
            input.value.trim();

        if (!message || isSending) {
            return;
        }

        hideError();

        addMessage(
            "user",
            message
        );

        input.value = "";
        resizeInput();
        updateCharacterCount();

        isSending = true;
        thinking.hidden = false;
        sendButton.disabled = true;
        micButton.disabled = true;

        status.textContent =
            "Thinking...";

        scrollMessagesToBottom();

        try {
            const historyForRequest =
                conversationHistory.slice(
                    0,
                    -1
                );

            const response = await fetch(
                "/api/ai-assistant/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",
                        "Accept":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message: message,
                        history:
                            historyForRequest
                    })
                }
            );

            const data =
                await response.json();

            if (!response.ok || !data.success) {
                throw new Error(
                    data.error ||
                    "AI response failed."
                );
            }

            userLanguageCode =
                data.languageCode ||
                userLanguageCode;

            addMessage(
                "assistant",
                data.reply
            );

            speakText(
                data.reply
            );

        } catch (error) {
            showError(
                error.message ||
                "Unable to get AI response."
            );

        } finally {
            isSending = false;
            thinking.hidden = true;
            micButton.disabled = false;
            status.textContent = "Online";

            updateCharacterCount();
        }
    }


    function setupSpeechRecognition() {
        const SpeechRecognition =
            window.SpeechRecognition ||
            window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            micButton.disabled = true;

            voiceStatus.textContent =
                "Voice input is not supported in this browser";

            return;
        }

        recognition =
            new SpeechRecognition();

        recognition.continuous = false;
        recognition.interimResults = true;

        recognition.lang =
            speechLanguageMap[userLanguageCode]
            || "en-IN";

        recognition.onstart = function () {
            isListening = true;

            micButton.classList.add(
                "is-listening"
            );

            micButton.innerHTML =
                '<i class="bi bi-stop-fill"></i>';

            voiceStatus.textContent =
                "Listening...";
        };

        recognition.onresult =
            function (event) {

                let finalText = "";
                let interimText = "";

                for (
                    let index =
                        event.resultIndex;
                    index <
                        event.results.length;
                    index++
                ) {
                    const transcript =
                        event.results[index][0]
                            .transcript;

                    if (
                        event.results[index]
                            .isFinal
                    ) {
                        finalText += transcript;
                    } else {
                        interimText += transcript;
                    }
                }

                const spokenText =
                    finalText ||
                    interimText;

                if (spokenText) {
                    input.value =
                        spokenText;

                    resizeInput();
                    updateCharacterCount();
                }
            };

        recognition.onerror =
            function (event) {

                stopListening();

                if (
                    event.error !==
                    "no-speech"
                ) {
                    showError(
                        "Voice input error: " +
                        event.error
                    );
                }
            };

        recognition.onend = function () {
            const shouldSend =
                isListening &&
                input.value.trim();

            stopListening();

            if (shouldSend) {
                setTimeout(
                    sendMessage,
                    180
                );
            }
        };
    }


    function startListening() {
        if (!recognition) {
            setupSpeechRecognition();
        }

        if (!recognition) {
            return;
        }

        if (
            "speechSynthesis" in window
        ) {
            window.speechSynthesis.cancel();
        }

        recognition.lang =
            speechLanguageMap[userLanguageCode]
            || "en-IN";

        try {
            recognition.start();
        } catch (error) {
            console.log(
                "Speech recognition already active."
            );
        }
    }


    function stopListening() {
        if (recognition && isListening) {
            try {
                recognition.stop();
            } catch (error) {
                console.log(error);
            }
        }

        isListening = false;

        micButton.classList.remove(
            "is-listening"
        );

        micButton.innerHTML =
            '<i class="bi bi-mic-fill"></i>';

        voiceStatus.textContent =
            "Type or tap microphone";
    }


    openButton.addEventListener(
        "click",
        openAssistant
    );

    closeButton.addEventListener(
        "click",
        closeAssistant
    );

    backdrop.addEventListener(
        "click",
        closeAssistant
    );

    clearButton.addEventListener(
        "click",
        clearConversation
    );

    voiceToggle.addEventListener(
        "click",
        function () {

            voiceReplyEnabled =
                !voiceReplyEnabled;

            voiceToggle.classList.toggle(
                "is-muted",
                !voiceReplyEnabled
            );

            voiceToggle.innerHTML =
                voiceReplyEnabled
                    ? '<i class="bi bi-volume-up-fill"></i>'
                    : '<i class="bi bi-volume-mute-fill"></i>';

            if (
                !voiceReplyEnabled &&
                "speechSynthesis" in window
            ) {
                window.speechSynthesis.cancel();

                character.classList.remove(
                    "is-speaking"
                );
                character.src =
                    idleImage;
            }
        }
    );

    micButton.addEventListener(
        "click",
        function () {

            if (isListening) {
                stopListening();
            } else {
                startListening();
            }
        }
    );

    sendButton.addEventListener(
        "click",
        sendMessage
    );

    input.addEventListener(
        "input",
        function () {
            resizeInput();
            updateCharacterCount();
        }
    );

    input.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {
                event.preventDefault();
                sendMessage();
            }
        }
    );

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape" &&
                !shell.hidden
            ) {
                closeAssistant();
            }
        }
    );

    updateCharacterCount();
});