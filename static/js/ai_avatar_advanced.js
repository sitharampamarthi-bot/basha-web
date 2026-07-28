console.log("BASHA ADVANCED AI JS LOADED");
document.addEventListener(
    "DOMContentLoaded",
    function () {

        function getElement(id) {
            return document.getElementById(id);
        }


        const openButton =
            getElement("bashaAiOpenButton");

        const topAvatar =
            getElement("bashaAiTopAvatar");

        const flyingAvatar =
            getElement("bashaAiFlyingAvatar");

        const shell =
            getElement("bashaAiShell");


        if (
            !openButton ||
            !topAvatar ||
            !flyingAvatar ||
            !shell
        ) {
            console.log(
                "Basha AI elements not found."
            );

            return;
        }


        const backdrop =
            getElement("bashaAiBackdrop");

        const closeButton =
            getElement("bashaAiCloseButton");

        const clearButton =
            getElement("bashaAiClearButton");

        const voiceToggle =
            getElement("bashaAiVoiceToggle");

        const character =
            getElement("bashaAiCharacter");

        const headerAvatar =
            getElement("bashaAiHeaderAvatar");

        const thinkingAvatar =
            getElement("bashaAiThinkingAvatar");

        const characterSection =
            getElement("bashaAiCharacterSection");

        const introBubble =
            getElement("bashaAiIntroBubble");

        const messages =
            getElement("bashaAiMessages");

        const thinking =
            getElement("bashaAiThinking");

        const errorBox =
            getElement("bashaAiError");

        const input =
            getElement("bashaAiInput");

        const micButton =
            getElement("bashaAiMicButton");

        const sendButton =
            getElement("bashaAiSendButton");

        const status =
            getElement("bashaAiStatus");

        const voiceStatus =
            getElement("bashaAiVoiceStatus");

        const characterCount =
            getElement("bashaAiCharacterCount");


        const avatarFrames = {

            idle: [
                shell.dataset.idle1,
                shell.dataset.idle2,
                shell.dataset.idle3
            ],

            blink: [
                shell.dataset.blink1,
                shell.dataset.blink2
            ],

            wave: [
                shell.dataset.wave1,
                shell.dataset.wave2,
                shell.dataset.wave3
            ],

            thinking: [
                shell.dataset.thinking1,
                shell.dataset.thinking2,
                shell.dataset.thinking3
            ],

            speaking: [
                shell.dataset.speaking1,
                shell.dataset.speaking2,
                shell.dataset.speaking3,
                shell.dataset.speaking4
            ],

            fallback:
                shell.dataset.fallbackSrc ||
                "/static/images/basha-ai-assistant.png"
        };

        let initialized = false;
        let isSending = false;
        let isAnimating = false;

        let recognition = null;
        let isListening = false;

        let userLanguageCode = "en";

        let conversationHistory = [];

        let greetingRunId = 0;

        let blinkTimer = null;

        let avatarAnimationTimer = null;

        let avatarState = "idle";

        let avatarFrameIndex = 0;


        let voiceReplyEnabled =
            localStorage.getItem(
                "bashaAiVoiceReply"
            ) !== "off";


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


        function wait(milliseconds) {
            return new Promise(
                function (resolve) {
                    window.setTimeout(
                        resolve,
                        milliseconds
                    );
                }
            );
        }


        function installImageFallbacks() {
            const images =
                document.querySelectorAll(
                    ".basha-ai-shell img," +
                    ".basha-ai-floating-button img," +
                    ".basha-ai-flying-avatar img"
                );


            images.forEach(
                function (image) {

                    image.addEventListener(
                        "error",
                        function () {

                            const fallbackSource =
                                image.dataset.fallbackSrc ||
                                avatarFrames.fallback;


                            if (!fallbackSource) {
                                return;
                            }


                            const fallbackUrl =
                                new URL(
                                    fallbackSource,
                                    window.location.href
                                ).href;


                            if (
                                image.src !== fallbackUrl
                            ) {
                                image.src =
                                    fallbackSource;
                            }

                        }
                    );

                }
            );
        }


        function preloadAvatarImages() {

            const allFrames = [
                ...avatarFrames.idle,
                ...avatarFrames.blink,
                ...avatarFrames.wave,
                ...avatarFrames.thinking,
                ...avatarFrames.speaking
            ];


            allFrames.forEach(
                function (imageSource) {

                    if (!imageSource) {
                        return;
                    }


                    const preloadImage =
                        new Image();


                    preloadImage.src =
                        imageSource;

                }
            );
        }


        function primeSpeechSynthesis() {
            if (
                !(
                    "speechSynthesis"
                    in window
                )
            ) {
                return;
            }

            window.speechSynthesis.resume();

            window.speechSynthesis.getVoices();
        }


        function getCurrentTime() {
            return new Intl.DateTimeFormat(
                [],
                {
                    hour: "2-digit",
                    minute: "2-digit"
                }
            ).format(
                new Date()
            );
        }


        function showError(message) {
            errorBox.textContent =
                message ||
                "Something went wrong.";

            errorBox.hidden = false;
        }


        function hideError() {
            errorBox.hidden = true;
            errorBox.textContent = "";
        }


        function scrollMessagesToBottom() {
            window.requestAnimationFrame(
                function () {

                    messages.scrollTop =
                        messages.scrollHeight;

                }
            );
        }


        function resizeInput() {
            input.style.height =
                "auto";

            input.style.height =
                Math.min(
                    input.scrollHeight,
                    130
                ) + "px";
        }


        function updateCharacterCount() {
            characterCount.textContent =
                input.value.length +
                " / 5000";

            sendButton.disabled =
                isSending ||
                !input.value.trim();
        }


        function setMainAvatarFrame(
            imageSource
        ) {

            if (!imageSource) {
                imageSource =
                    avatarFrames.fallback;
            }


            character.src =
                imageSource;
        }


        function stopAvatarAnimation() {

            if (avatarAnimationTimer) {

                window.clearInterval(
                    avatarAnimationTimer
                );


                avatarAnimationTimer =
                    null;
            }


            avatarFrameIndex =
                0;
        }


        function removeAvatarClasses() {

            character.classList.remove(
                "is-speaking",
                "is-thinking",
                "is-wave",
                "is-blinking"
            );
        }


        function playAvatarFrames(
            state,
            options
        ) {

            const settings =
                options || {};


            const frames =
                avatarFrames[state];


            if (
                !frames ||
                !frames.length
            ) {
                return;
            }


            stopAvatarAnimation();

            removeAvatarClasses();


            avatarState =
                state;


            avatarFrameIndex =
                0;


            const speed =
                settings.speed || 250;


            const loop =
                settings.loop !== false;


            const returnToIdle =
                settings.returnToIdle !== false;


            if (state === "speaking") {

                character.classList.add(
                    "is-speaking"
                );

            } else if (
                state === "thinking"
            ) {

                character.classList.add(
                    "is-thinking"
                );

            } else if (
                state === "wave"
            ) {

                character.classList.add(
                    "is-wave"
                );

            } else if (
                state === "blink"
            ) {

                character.classList.add(
                    "is-blinking"
                );
            }


            setMainAvatarFrame(
                frames[0]
            );


            avatarAnimationTimer =
                window.setInterval(
                    function () {

                        avatarFrameIndex++;


                        if (
                            avatarFrameIndex >=
                            frames.length
                        ) {

                            if (loop) {

                                avatarFrameIndex =
                                    0;

                            } else {

                                stopAvatarAnimation();


                                if (
                                    returnToIdle
                                ) {

                                    playAvatarFrames(
                                        "idle",
                                        {
                                            speed: 650,
                                            loop: true,
                                            returnToIdle: false
                                        }
                                    );

                                }


                                return;
                            }
                        }


                        setMainAvatarFrame(
                            frames[
                                avatarFrameIndex
                            ]
                        );

                    },
                    speed
                );
        }


        function setAvatarState(
            state
        ) {

            if (state === "idle") {

                playAvatarFrames(
                    "idle",
                    {
                        speed: 650,
                        loop: true,
                        returnToIdle: false
                    }
                );

                return;
            }


            if (state === "blink") {

                playAvatarFrames(
                    "blink",
                    {
                        speed: 120,
                        loop: false,
                        returnToIdle: true
                    }
                );

                return;
            }


            if (state === "wave") {

                playAvatarFrames(
                    "wave",
                    {
                        speed: 260,
                        loop: false,
                        returnToIdle: true
                    }
                );

                return;
            }


            if (state === "thinking") {

                playAvatarFrames(
                    "thinking",
                    {
                        speed: 300,
                        loop: true,
                        returnToIdle: false
                    }
                );

                return;
            }


            if (state === "speaking") {

                playAvatarFrames(
                    "speaking",
                    {
                        speed: 145,
                        loop: true,
                        returnToIdle: false
                    }
                );
            }
        }


        function resetAssistantVisuals() {

            setAvatarState(
                "idle"
            );


            status.textContent =
                "Online";
        }


        function scheduleBlink() {

            window.clearTimeout(
                blinkTimer
            );


            const nextBlinkTime =
                3500 +
                Math.random() * 3000;


            blinkTimer =
                window.setTimeout(
                    function () {

                        const canBlink =
                            !shell.hidden &&
                            !isSending &&
                            !isListening &&
                            avatarState === "idle";


                        if (canBlink) {

                            setAvatarState(
                                "blink"
                            );
                        }


                        scheduleBlink();

                    },
                    nextBlinkTime
                );
        }


        function createMessage(
            role,
            text
        ) {
            const row =
                document.createElement(
                    "div"
                );


            row.className =
                "basha-ai-message-row " +
                (
                    role === "user"
                        ? "is-user"
                        : "is-assistant"
                );


            const bubble =
                document.createElement(
                    "div"
                );


            bubble.className =
                "basha-ai-message";


            const content =
                document.createElement(
                    "span"
                );


            const time =
                document.createElement(
                    "span"
                );


            time.className =
                "basha-ai-message-time";


            time.textContent =
                getCurrentTime();


            bubble.appendChild(
                content
            );


            bubble.appendChild(
                time
            );


            row.appendChild(
                bubble
            );


            messages.appendChild(
                row
            );


            conversationHistory.push({
                role: role,
                text: text
            });


            if (
                conversationHistory.length > 20
            ) {
                conversationHistory =
                    conversationHistory.slice(
                        -20
                    );
            }


            scrollMessagesToBottom();


            return content;
        }


        async function addMessage(
            role,
            text,
            useTypewriter
        ) {
            const contentElement =
                createMessage(
                    role,
                    text
                );


            if (!useTypewriter) {
                contentElement.textContent =
                    text;

                scrollMessagesToBottom();

                return;
            }


            const fullText =
                String(text || "");


            for (
                const letter of fullText
            ) {
                contentElement.textContent +=
                    letter;

                scrollMessagesToBottom();

                await wait(12);
            }
        }


        function chooseSpeechVoice(
            languageTag
        ) {
            const availableVoices =
                window.speechSynthesis.getVoices();


            if (
                !availableVoices.length
            ) {
                return null;
            }


            const normalizedTag =
                String(
                    languageTag || ""
                ).toLowerCase();


            const languagePrefix =
                normalizedTag.split("-")[0];


            return (
                availableVoices.find(
                    function (voice) {
                        return (
                            voice.lang.toLowerCase()
                            === normalizedTag
                        );
                    }
                )

                ||

                availableVoices.find(
                    function (voice) {
                        return voice.lang
                            .toLowerCase()
                            .startsWith(
                                languagePrefix
                            );
                    }
                )

                ||

                availableVoices.find(
                    function (voice) {
                        return voice.lang
                            .toLowerCase()
                            .startsWith("en");
                    }
                )

                ||

                null
            );
        }


        function speakText(text) {
            return new Promise(
                function (resolve) {

                    if (
                        !voiceReplyEnabled ||
                        !(
                            "speechSynthesis"
                            in window
                        ) ||
                        !text
                    ) {
                        resetAssistantVisuals();

                        resolve();

                        return;
                    }


                    window.speechSynthesis.cancel();

                    window.speechSynthesis.resume();


                    const utterance =
                        new SpeechSynthesisUtterance(
                            text
                        );


                    utterance.lang =
                        speechLanguageMap[
                            userLanguageCode
                        ]
                        ||
                        userLanguageCode
                        ||
                        "en-IN";


                    utterance.rate = 0.90;
                    utterance.pitch = 1;
                    utterance.volume = 1;


                    utterance.voice =
                        chooseSpeechVoice(
                            utterance.lang
                        );


                    utterance.onstart =
                        function () {

                            setAvatarState(
                                "speaking"
                            );


                            status.textContent =
                                "Laxmi is speaking...";


                            voiceStatus.textContent =
                                "Laxmi is speaking...";

                        };


                    utterance.onend =
                        function () {

                            resetAssistantVisuals();


                            voiceStatus.textContent =
                                "Type or tap microphone";


                            resolve();

                        };


                    utterance.onerror =
                        function (event) {

                            console.log(
                                "Laxmi TTS error:",
                                event
                            );


                            resetAssistantVisuals();


                            voiceStatus.textContent =
                                "Voice could not play";


                            resolve();

                        };


                    window.speechSynthesis.speak(
                        utterance
                    );


                    /*
                    Chrome long speech pause problem fix.
                    */

                    const keepAliveInterval =
                        window.setInterval(
                            function () {

                                if (
                                    !window.speechSynthesis
                                        .speaking
                                ) {
                                    window.clearInterval(
                                        keepAliveInterval
                                    );

                                    return;
                                }


                                window.speechSynthesis.pause();

                                window.speechSynthesis.resume();

                            },
                            10000
                        );

                }
            );
        }


        async function typeGreeting(text) {
            const currentRunId =
                ++greetingRunId;


            introBubble.textContent =
                "";


            const greetingText =
                String(text || "");


            for (
                const letter
                of greetingText
            ) {
                if (
                    currentRunId
                    !== greetingRunId
                ) {
                    return;
                }


                introBubble.textContent +=
                    letter;


                await wait(18);
            }
        }


        async function loadGreeting() {
            introBubble.classList.add(
                "show"
            );


            introBubble.innerHTML = `
                <span class="basha-ai-intro-loading">
                    <span></span>
                    <span></span>
                    <span></span>
                </span>
            `;


            try {
                const response =
                    await fetch(
                        "/api/ai-assistant/greeting",
                        {
                            method: "GET",

                            credentials:
                                "same-origin",

                            headers: {
                                "Accept":
                                    "application/json"
                            }
                        }
                    );


                const data =
                    await response.json();


                if (
                    !response.ok ||
                    !data.success
                ) {
                    throw new Error(
                        data.error ||
                        "Unable to load assistant."
                    );
                }


                userLanguageCode =
                    data.languageCode ||
                    "en";


                setupSpeechRecognition();


                setAvatarState(
                    "wave"
                );

                await wait(900);

                await typeGreeting(
                    data.greeting
                );


                await wait(220);


                await speakText(
                    data.greeting
                );


                status.textContent =
                    "Ready";


                voiceStatus.textContent =
                    "Tap microphone or type your question";

            } catch (error) {

                const fallbackGreeting =
                    "Hi 👋 I am Basha AI Assistant. How can I help you?";


                await typeGreeting(
                    fallbackGreeting
                );


                showError(
                    error.message
                );
            }
        }


        function getTargetCharacterRect() {
            const sectionRect =
                characterSection
                    .getBoundingClientRect();


            const isMobile =
                window.innerWidth <= 600;


            const size =
                isMobile
                    ? 88
                    : 102;


            return {
                left:
                    sectionRect.left +
                    (
                        isMobile
                            ? 27
                            : 48
                    ),

                top:
                    sectionRect.bottom -
                    size -
                    (
                        isMobile
                            ? 32
                            : 44
                    ),

                width:
                    size,

                height:
                    size
            };
        }


        function setFlyingAvatarRect(
            rectangle
        ) {
            flyingAvatar.style.left =
                rectangle.left + "px";

            flyingAvatar.style.top =
                rectangle.top + "px";

            flyingAvatar.style.width =
                rectangle.width + "px";

            flyingAvatar.style.height =
                rectangle.height + "px";
        }


        async function animateOpen() {

            console.log(
                "AI OPEN FUNCTION STARTED"
            );


            if (isAnimating) {
                return;
            }


            isAnimating = true;


            primeSpeechSynthesis();

            hideError();

            stopListening();

            const flyingImage =
                flyingAvatar.querySelector(
                    "img"
                );

            if (flyingImage) {

                flyingImage.src =
                    avatarFrames.idle[0] ||
                    avatarFrames.fallback;
            }

            shell.hidden = false;

            shell.classList.remove(
                "is-open",
                "character-ready"
            );

            introBubble.classList.remove(
                "show"
            );

            resetAssistantVisuals();

            const startRect =
                topAvatar.getBoundingClientRect();

            console.log(
                "AI START RECT:",
                startRect
            );

            setFlyingAvatarRect(
                startRect
            );

            flyingAvatar.hidden = false;

            openButton.classList.add(
                "is-hidden"
            );

            await wait(30);

            shell.classList.add(
                "is-open"
            );

            document.body.style.overflow =
                "hidden";

            await wait(100);

            const destination =
                getTargetCharacterRect();

            const deltaX =
                destination.left -
                startRect.left;

            const deltaY =
                destination.top -
                startRect.top;

            const scaleX =
                destination.width /
                Math.max(
                    startRect.width,
                    1
                );

            const scaleY =
                destination.height /
                Math.max(
                    startRect.height,
                    1
                );

            try {

                if (
                    typeof flyingAvatar.animate
                    === "function"
                ) {
                    const animation =
                        flyingAvatar.animate(
                            [
                                {
                                    transform:
                                        "translate(0px, 0px) scale(1)",

                                    opacity:
                                        1
                                },

                                {
                                    transform:
                                        "translate(" +
                                        (deltaX * 0.55) +
                                        "px, " +
                                        (deltaY * 0.25) +
                                        "px) scale(1.32) rotate(-8deg)",

                                    opacity:
                                        1,

                                    offset:
                                        0.45
                                },

                                {
                                    transform:
                                        "translate(" +
                                        deltaX +
                                        "px, " +
                                        deltaY +
                                        "px) scale(" +
                                        scaleX +
                                        ", " +
                                        scaleY +
                                        ") rotate(0deg)",

                                    opacity:
                                        1
                                }
                            ],

                            {
                                duration:
                                    760,

                                easing:
                                    "cubic-bezier(.18,.84,.32,1)",

                                fill:
                                    "forwards"
                            }
                        );


                    await animation.finished;

                } else {

                    console.log(
                        "Web Animations API unavailable. Opening without fly animation."
                    );

                    await wait(250);
                }

            } catch (error) {

                console.log(
                    "AI open animation error:",
                    error
                );

            }

            flyingAvatar.hidden = true;

            shell.classList.add(
                "character-ready"
            );

            introBubble.classList.add(
                "show"
            );

            isAnimating = false;

            scheduleBlink();

            window.setTimeout(
                function () {
                    input.focus();
                },
                120
            );

            if (!initialized) {

                initialized = true;

                loadGreeting();

            }

        }

        async function animateClose() {
            if (
                isAnimating ||
                shell.hidden
            ) {
                return;
            }

            isAnimating = true;

            stopAvatarAnimation();

            greetingRunId++;

            window.clearTimeout(
                blinkTimer
            );

            if (
                "speechSynthesis"
                in window
            ) {
                window.speechSynthesis.cancel();
            }

            stopListening();

            resetAssistantVisuals();

            const characterRect =
                character
                    .getBoundingClientRect();

            const startSize =
                Math.min(
                    characterRect.width,
                    characterRect.height,
                    105
                );

            const startRect = {
                left:
                    characterRect.left +
                    (
                        characterRect.width -
                        startSize
                    ) / 2,

                top:
                    characterRect.top +
                    (
                        characterRect.height -
                        startSize
                    ) / 2,

                width:
                    startSize,

                height:
                    startSize
            };


            const destination =
                topAvatar
                    .getBoundingClientRect();


            setFlyingAvatarRect(
                startRect
            );

            flyingAvatar.hidden =
                false;


            shell.classList.remove(
                "character-ready"
            );

            introBubble.classList.remove(
                "show"
            );

            await wait(30);

            shell.classList.remove(
                "is-open"
            );

            const deltaX =
                destination.left -
                startRect.left;

            const deltaY =
                destination.top -
                startRect.top;

            const scaleX =
                destination.width /
                startRect.width;

            const scaleY =
                destination.height /
                startRect.height;

            const animation =
                flyingAvatar.animate(
                    [
                        {
                            transform:
                                "translate(0,0) scale(1)",

                            opacity: 1
                        },

                        {
                            transform:
                                `translate(
                                    ${deltaX * .55}px,
                                    ${deltaY * .75}px
                                )
                                scale(.82)
                                rotate(7deg)`,

                            opacity: 1,

                            offset: .55
                        },

                        {
                            transform:
                                `translate(
                                    ${deltaX}px,
                                    ${deltaY}px
                                )
                                scale(
                                    ${scaleX},
                                    ${scaleY}
                                )
                                rotate(0deg)`,

                            opacity: .96
                        }
                    ],

                    {
                        duration: 620,

                        easing:
                            "cubic-bezier(.4,0,.2,1)",

                        fill:
                            "forwards"
                    }
                );

            try {
                await animation.finished;
            } catch (error) {
                console.log(
                    "AI close animation cancelled."
                );
            }

            flyingAvatar.hidden =
                true;

            shell.hidden =
                true;

            openButton.classList.remove(
                "is-hidden"
            );

            document.body.style.overflow =
                "";

            isAnimating =
                false;
        }

        function clearConversation() {
            conversationHistory = [];

            messages.innerHTML = "";

            input.value = "";

            resizeInput();

            updateCharacterCount();

            hideError();

            greetingRunId++;

            if (
                "speechSynthesis"
                in window
            ) {
                window.speechSynthesis.cancel();
            }

            stopAvatarAnimation();

            resetAssistantVisuals();

            loadGreeting();
        }

        async function sendMessage() {
            const message =
                input.value.trim();

            if (
                !message ||
                isSending
            ) {
                return;
            }

            hideError();

            await addMessage(
                "user",
                message,
                false
            );

            input.value = "";

            resizeInput();

            isSending = true;

            updateCharacterCount();

            thinking.hidden = false;

            micButton.disabled = true;

            status.textContent =
                "Thinking...";

            setAvatarState(
                "thinking"
            );

            scrollMessagesToBottom();

            try {
                const historyForRequest =
                    conversationHistory.slice(
                        0,
                        -1
                    );

                const response =
                    await fetch(
                        "/api/ai-assistant/chat",

                        {
                            method:
                                "POST",

                            credentials:
                                "same-origin",

                            headers: {
                                "Content-Type":
                                    "application/json",

                                "Accept":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({
                                    message:
                                        message,

                                    history:
                                        historyForRequest
                                })
                        }
                    );

                const data =
                    await response.json();

                if (
                    !response.ok ||
                    !data.success
                ) {
                    throw new Error(
                        data.error ||
                        "AI response failed."
                    );
                }

                userLanguageCode =
                    data.languageCode ||
                    userLanguageCode;


                thinking.hidden =
                    true;


                await addMessage(
                    "assistant",
                    data.reply,
                    true
                );


                await speakText(
                    data.reply
                );

            } catch (error) {

                showError(
                    error.message ||
                    "Unable to get AI response."
                );

            } finally {

                isSending =
                    false;


                thinking.hidden =
                    true;


                micButton.disabled =
                    false;


                if (
                    !character.classList.contains(
                        "is-speaking"
                    )
                ) {
                    resetAssistantVisuals();
                }


                updateCharacterCount();
            }
        }


        function setupSpeechRecognition() {
            const SpeechRecognition =
                window.SpeechRecognition ||
                window.webkitSpeechRecognition;


            if (!SpeechRecognition) {
                micButton.disabled =
                    true;


                voiceStatus.textContent =
                    "Voice input is not supported in this browser";


                return;
            }


            recognition =
                new SpeechRecognition();


            recognition.continuous =
                false;


            recognition.interimResults =
                true;


            recognition.lang =
                speechLanguageMap[
                    userLanguageCode
                ]
                ||
                "en-IN";


            recognition.onstart =
                function () {

                    isListening = true;


                    micButton.classList.add(
                        "is-listening"
                    );


                    micButton.innerHTML =
                        '<i class="bi bi-stop-fill"></i>';


                    voiceStatus.textContent =
                        "Listening...";


                    status.textContent =
                        "Listening...";

                };


            recognition.onresult =
                function (event) {

                    let finalText =
                        "";

                    let interimText =
                        "";


                    for (
                        let index =
                            event.resultIndex;

                        index <
                            event.results.length;

                        index++
                    ) {
                        const transcript =
                            event.results[
                                index
                            ][0].transcript;


                        if (
                            event.results[
                                index
                            ].isFinal
                        ) {
                            finalText +=
                                transcript;
                        } else {
                            interimText +=
                                transcript;
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


            recognition.onend =
                function () {

                    const shouldSend =
                        isListening &&
                        input.value.trim();


                    stopListening();


                    if (shouldSend) {
                        window.setTimeout(
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
                "speechSynthesis"
                in window
            ) {
                window.speechSynthesis.cancel();
            }


            setAvatarState(
                "idle"
            );


            recognition.lang =
                speechLanguageMap[
                    userLanguageCode
                ]
                ||
                "en-IN";


            try {
                recognition.start();
            } catch (error) {
                console.log(
                    "Speech recognition already active."
                );
            }
        }


        function stopListening() {
            if (
                recognition &&
                isListening
            ) {
                try {
                    recognition.stop();
                } catch (error) {
                    console.log(error);
                }
            }


            isListening =
                false;


            micButton.classList.remove(
                "is-listening"
            );


            micButton.innerHTML =
                '<i class="bi bi-mic-fill"></i>';


            voiceStatus.textContent =
                "Type or tap microphone";


            if (!isSending) {
                status.textContent =
                    "Online";
            }
        }


        openButton.addEventListener(
            "click",
            animateOpen
        );


        closeButton.addEventListener(
            "click",
            animateClose
        );


        backdrop.addEventListener(
            "click",
            animateClose
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


                localStorage.setItem(
                    "bashaAiVoiceReply",

                    voiceReplyEnabled
                        ? "on"
                        : "off"
                );


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
                    "speechSynthesis"
                    in window
                ) {
                    window.speechSynthesis.cancel();

                    resetAssistantVisuals();
                } else {
                    primeSpeechSynthesis();
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
                    animateClose();
                }

            }
        );


        window.addEventListener(
            "beforeunload",
            function () {

                if (
                    "speechSynthesis"
                    in window
                ) {
                    window.speechSynthesis.cancel();
                }

            }
        );


        if (
            "speechSynthesis"
            in window
        ) {
            window.speechSynthesis.onvoiceschanged =
                function () {

                    window.speechSynthesis.getVoices();

                };
        }


        installImageFallbacks();

        preloadAvatarImages();


        headerAvatar.src =
            avatarFrames.idle[0] ||
            avatarFrames.fallback;


        thinkingAvatar.src =
            avatarFrames.thinking[0] ||
            avatarFrames.fallback;


        setMainAvatarFrame(
            avatarFrames.idle[0] ||
            avatarFrames.fallback
        );


        setAvatarState(
            "idle"
        );


        voiceToggle.classList.toggle(
            "is-muted",
            !voiceReplyEnabled
        );


        voiceToggle.innerHTML =
            voiceReplyEnabled

                ? '<i class="bi bi-volume-up-fill"></i>'

                : '<i class="bi bi-volume-mute-fill"></i>';


        updateCharacterCount();

    }
);