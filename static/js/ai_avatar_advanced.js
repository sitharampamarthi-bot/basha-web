"use strict";

console.log("BASHA ADVANCED AI JS LOADED");

document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       ELEMENTS
    ===================================================== */

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
            "Basha AI required elements not found."
        );

        return;
    }

    const panel =
        getElement("bashaAiPanel");

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

    const audioPlayer =
        getElement("bashaAiAudioPlayer");    


    /* =====================================================
       AVATAR IMAGE FRAMES
    ===================================================== */

    const avatarFrames = {

        idle: [
            shell.dataset.idle1,
            shell.dataset.idle2,
            shell.dataset.idle3,
            shell.dataset.idle4
        ].filter(Boolean),

        blink: [
            shell.dataset.blink1,
            shell.dataset.blink2
        ].filter(Boolean),

        wave: [
            shell.dataset.wave1,
            shell.dataset.wave2,
            shell.dataset.wave3,
            shell.dataset.wave4,
            shell.dataset.wave5
        ].filter(Boolean),

        thinking: [
            shell.dataset.thinking1,
            shell.dataset.thinking2,
            shell.dataset.thinking3,
            shell.dataset.thinking4,
            shell.dataset.thinking5
        ].filter(Boolean),

        speaking: [
            shell.dataset.speaking1,
            shell.dataset.speaking2,
            shell.dataset.speaking3,
            shell.dataset.speaking4
        ].filter(Boolean),

        explaining: [
            shell.dataset.explaining1,
            shell.dataset.explaining2,
            shell.dataset.explaining3,
            shell.dataset.explaining4,
            shell.dataset.explaining5
        ].filter(Boolean),

        fallback:
            shell.dataset.fallbackSrc ||
            "/static/images/ai/idle-1.png"
    };


    /* =====================================================
       STATE
    ===================================================== */

    let initialized = false;

    let hasWelcomed = false;

    let currentAudio = null;

    let currentRequest = null;

    let recognition = null;

    let voiceSilenceTimer = null;

    let accumulatedVoiceText = "";

    let recognitionShouldRestart = false;

    let isSpeaking = false;

    let isThinking = false;

    let chatHistory = [];

    let lastVoiceBlob = null;

    let isSending = false;

    let isAnimating = false;

    let isListening = false;

    let lastFinalTranscript = "";

    let iosMediaRecorder = null;

    let iosMediaStream = null;

    let iosAudioChunks = [];

    let iosRecordingTimer = null;

    let iosMaximumTimer = null;

    let iosRecordingStartedAt = 0;

    let iosIsRecording = false;

    let iosTranscriptionController = null;

    const IOS_RECORDING_DELAY = 5000;

    const IOS_MAXIMUM_RECORDING_TIME = 60000;

    let userLanguageCode = "en";

    let conversationHistory = [];

    let currentChatController = null;

    let currentTtsController = null;

    let currentSpeechCancel = null;

    let greetingRunId = 0;

    let blinkTimer = null;

    let avatarAnimationTimer = null;

    let avatarState = "idle";

    let avatarFrameIndex = 0;

    let speechKeepAliveTimer = null;

    let pageIsVisible =
        document.visibilityState === "visible";

    let voiceReplyEnabled =
        localStorage.getItem("bashaAiVoiceReply") !== "off";

    const VOICE_SILENCE_DELAY = 3000;

    const AI_REPLY_DELAY = 2000;    

    /* =====================================================
       LANGUAGE MAP
    ===================================================== */

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
        ne: "ne-NP",

        ar: "ar-SA",
        fr: "fr-FR",
        de: "de-DE",
        es: "es-ES",
        pt: "pt-BR",
        ru: "ru-RU",
        ja: "ja-JP",
        ko: "ko-KR",
        zh: "zh-CN"

    };


    /* =====================================================
       GENERAL HELPERS
    ===================================================== */

    function isIOSDevice() {

        return (
            /iPad|iPhone|iPod/i.test(
                navigator.userAgent
            ) ||
            (
                navigator.platform === "MacIntel" &&
                navigator.maxTouchPoints > 1
            )
        );

    }

    function supportsMediaRecorder() {

        return Boolean(
            navigator.mediaDevices &&
            navigator.mediaDevices.getUserMedia &&
            window.MediaRecorder
        );

    }


    function getSupportedAudioMimeType() {

        const types = [
            "audio/mp4",
            "audio/webm;codecs=opus",
            "audio/webm",
            "audio/ogg;codecs=opus"
        ];

        for (const type of types) {

            if (
                window.MediaRecorder &&
                typeof MediaRecorder.isTypeSupported ===
                    "function" &&
                MediaRecorder.isTypeSupported(type)
            ) {

                return type;

            }

        }

        return "";

    }


    function getAudioFileExtension(
        mimeType
    ) {

        const type =
            String(mimeType || "")
                .toLowerCase();

        if (type.includes("mp4")) {
            return "m4a";
        }

        if (type.includes("ogg")) {
            return "ogg";
        }

        if (type.includes("wav")) {
            return "wav";
        }

        return "webm";

    }


    function releaseIOSMediaStream() {

        if (!iosMediaStream) {
            return;
        }

        iosMediaStream
            .getTracks()
            .forEach(
                function (track) {

                    try {

                        track.stop();

                    } catch (error) {

                        console.log(
                            "iPhone track stop error:",
                            error
                        );

                    }

                }
            );

        iosMediaStream = null;

    }


    function clearIOSRecordingTimers() {

        if (iosRecordingTimer) {

            window.clearTimeout(
                iosRecordingTimer
            );

            iosRecordingTimer = null;

        }

        if (iosMaximumTimer) {

            window.clearTimeout(
                iosMaximumTimer
            );

            iosMaximumTimer = null;

        }

    }


    function updateIOSMicUI(
        recording
    ) {

        iosIsRecording =
            Boolean(recording);

        isListening =
            Boolean(recording);

        if (!micButton) {
            return;
        }

        micButton.classList.toggle(
            "is-listening",
            iosIsRecording
        );

        micButton.innerHTML =
            iosIsRecording

                ? '<i class="bi bi-stop-fill"></i>'

                : '<i class="bi bi-mic-fill"></i>';

        micButton.setAttribute(
            "aria-label",
            iosIsRecording
                ? "Stop recording"
                : "Start recording"
        );

    }

    function wait(milliseconds) {

        return new Promise(function (resolve) {

            window.setTimeout(
                resolve,
                milliseconds
            );

        });

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

        if (!errorBox) {
            return;
        }

        errorBox.textContent =
            message ||
            "Something went wrong.";

        errorBox.hidden = false;

    }


    function hideError() {

        if (!errorBox) {
            return;
        }

        errorBox.hidden = true;

        errorBox.textContent = "";

    }


    function scrollMessagesToBottom() {

        if (!messages) {
            return;
        }

        window.requestAnimationFrame(
            function () {

                messages.scrollTop =
                    messages.scrollHeight;

            }
        );

    }

    function updateAiMobileViewport() {

        const viewport =
            window.visualViewport;

        const visibleHeight =
            viewport
                ? viewport.height
                : window.innerHeight;

        document.documentElement.style.setProperty(
            "--basha-ai-visible-height",
            `${Math.round(
                visibleHeight
            )}px`
        );

        if (
            document.activeElement ===
            input
        ) {

            window.setTimeout(
                function () {

                    scrollMessagesToBottom();

                    input.scrollIntoView({
                        block: "nearest",
                        behavior: "smooth"
                    });

                },
                120
            );

        }

    }


    function resizeInput() {

        if (!input) {
            return;
        }

        input.style.height =
            "auto";

        input.style.height =
            Math.min(
                input.scrollHeight,
                130
            ) + "px";

    }


    function updateCharacterCount() {

        if (
            !characterCount ||
            !input ||
            !sendButton
        ) {
            return;
        }

        characterCount.textContent =
            input.value.length +
            " / 5000";

        sendButton.disabled =
            isSending ||
            !input.value.trim();

    }


    /* =====================================================
       IMAGE FALLBACK
    ===================================================== */

    function installImageFallbacks() {

        const images =
            document.querySelectorAll(
                ".basha-ai-shell img," +
                ".basha-ai-floating-button img," +
                ".basha-ai-flying-avatar img"
            );

        images.forEach(function (image) {

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

        });

    }


    function preloadAvatarImages() {

        const allFrames = [

            ...avatarFrames.idle,
            ...avatarFrames.blink,
            ...avatarFrames.wave,
            ...avatarFrames.thinking,
            ...avatarFrames.speaking,
            ...avatarFrames.explaining

        ];

        allFrames.forEach(
            function (imageSource) {

                if (!imageSource) {
                    return;
                }

                const image =
                    new Image();

                image.src =
                    imageSource;

            }
        );

    }


    /* =====================================================
       AVATAR ANIMATION
    ===================================================== */

    function setMainAvatarFrame(
        imageSource
    ) {

        if (!character) {
            return;
        }

        character.src =
            imageSource ||
            avatarFrames.fallback;

    }


    function setHeaderAvatarFrame(
        imageSource
    ) {

        if (!headerAvatar) {
            return;
        }

        headerAvatar.src =
            imageSource ||
            avatarFrames.fallback;

    }


    function stopAvatarAnimation() {

        if (avatarAnimationTimer) {

            window.clearInterval(
                avatarAnimationTimer
            );

            avatarAnimationTimer =
                null;

        }

        avatarFrameIndex = 0;

    }


    function removeAvatarClasses() {

        if (!character) {
            return;
        }

        character.classList.remove(
            "is-idle",
            "is-speaking",
            "is-thinking",
            "is-explaining",
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
            frames.length === 0
        ) {

            setMainAvatarFrame(
                avatarFrames.fallback
            );

            return;

        }

        stopAvatarAnimation();

        removeAvatarClasses();

        avatarState = state;

        avatarFrameIndex = 0;

        const speed =
            Number(settings.speed) ||
            250;

        const loop =
            settings.loop !== false;

        const returnToIdle =
            settings.returnToIdle !== false;

        character.classList.add(
            "is-" + state
        );

        setMainAvatarFrame(
            frames[0]
        );

        if (
            state === "thinking" &&
            thinkingAvatar
        ) {

            thinkingAvatar.src =
                frames[0];

        }

        avatarAnimationTimer =
            window.setInterval(
                function () {

                    if (
                        !pageIsVisible &&
                        state !== "speaking"
                    ) {
                        return;
                    }

                    avatarFrameIndex++;

                    if (
                        avatarFrameIndex >=
                        frames.length
                    ) {

                        if (loop) {

                            avatarFrameIndex = 0;

                        } else {

                            stopAvatarAnimation();

                            if (returnToIdle) {

                                setAvatarState(
                                    "idle"
                                );

                            }

                            return;

                        }

                    }

                    const frame =
                        frames[
                            avatarFrameIndex
                        ];

                    setMainAvatarFrame(
                        frame
                    );

                    if (
                        state === "thinking" &&
                        thinkingAvatar
                    ) {

                        thinkingAvatar.src =
                            frame;

                    }

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
                    speed: 620,
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
                    speed: 115,
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
                    speed: 220,
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
                    speed: 270,
                    loop: true,
                    returnToIdle: false
                }
            );

            return;

        }

        if (state === "explaining") {

            playAvatarFrames(
                "explaining",
                {
                    speed: 230,
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

        if (status) {

            status.textContent =
                "Online";

        }

    }


    function scheduleBlink() {

        if (blinkTimer) {

            window.clearTimeout(
                blinkTimer
            );

        }

        const nextBlinkTime =
            3500 +
            Math.random() * 3500;

        blinkTimer =
            window.setTimeout(
                function () {

                    const canBlink =

                        pageIsVisible &&
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


    /* =====================================================
       CHAT MESSAGES
    ===================================================== */

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

        content.className =
            "basha-ai-message-content";

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
            conversationHistory.length >
            20
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

        const fullText =
            String(text || "");

        if (!useTypewriter) {

            contentElement.textContent =
                fullText;

            scrollMessagesToBottom();

            return;

        }

        if (role === "assistant") {

            setAvatarState(
                "explaining"
            );

            if (status) {

                status.textContent =
                    "Laxmi is explaining...";

            }

        }

        for (
            const letter of fullText
        ) {

            contentElement.textContent +=
                letter;

            scrollMessagesToBottom();

            await wait(11);

        }

    }


    /* =====================================================
       SPEECH SYNTHESIS / TTS
    ===================================================== */

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


    function stopSpeechKeepAlive() {

        if (speechKeepAliveTimer) {

            window.clearInterval(
                speechKeepAliveTimer
            );

            speechKeepAliveTimer =
                null;

        }

    }

    function stopCurrentAssistantActivity() {

                clearIOSRecordingTimers();

        if (iosTranscriptionController) {

            iosTranscriptionController.abort();

            iosTranscriptionController =
                null;

        }

        if (
            iosMediaRecorder &&
            iosMediaRecorder.state !==
                "inactive"
        ) {

            try {

                iosMediaRecorder.onstop =
                    null;

                iosMediaRecorder.stop();

            } catch (error) {

                console.log(
                    "iPhone recorder stop error:",
                    error
                );

            }

        }

        iosMediaRecorder = null;

        iosAudioChunks = [];

        iosRecordingStartedAt = 0;

        updateIOSMicUI(
            false
        );

        releaseIOSMediaStream();

        /*
        * Stop current AI chat request.
        */
        if (currentChatController) {

            currentChatController.abort();

            currentChatController = null;

        }

        /*
        * Stop current TTS request.
        */
        if (currentTtsController) {

            currentTtsController.abort();

            currentTtsController = null;

        }

        /*
        * Resolve current speech promise safely.
        */
        if (currentSpeechCancel) {

            currentSpeechCancel();

            currentSpeechCancel = null;

        }

        /*
        * Stop Google Cloud audio.
        */
        if (audioPlayer) {

            audioPlayer.pause();

            audioPlayer.currentTime = 0;

            audioPlayer.onloadedmetadata = null;

            audioPlayer.onended = null;

            audioPlayer.onerror = null;

            audioPlayer.removeAttribute(
                "src"
            );

            audioPlayer.load();

        }

        /*
        * Stop browser speech fallback.
        */
        stopSpeechKeepAlive();

        if (
            "speechSynthesis"
            in window
        ) {

            window.speechSynthesis.cancel();

        }

        /*
        * Fully reset microphone recognition.
        */

        recognitionShouldRestart = false;

        clearVoiceSilenceTimer();

        accumulatedVoiceText = "";

        if (recognition) {

            try {

                recognition.abort();

            } catch (error) {

                console.log(
                    "Recognition abort error:",
                    error
                );

            }

            recognition = null;

        }

        isListening = false;

        isSending = false;

        isSpeaking = false;

        lastFinalTranscript = "";

        thinking.hidden = true;

        micButton.disabled = false;

        micButton.classList.remove(
            "is-listening"
        );

        micButton.innerHTML =
            '<i class="bi bi-mic-fill"></i>';

        characterSection.classList.remove(
            "is-speaking"
        );

        voiceStatus.textContent =
            "Type or tap microphone";

        resetAssistantVisuals();

        updateCharacterCount();

    }

    function chooseSpeechVoice(
        languageTag
    ) {

        if (
            !(
                "speechSynthesis"
                in window
            )
        ) {
            return null;
        }

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

        const exactVoice =
            availableVoices.find(
                function (voice) {

                    return (
                        voice.lang.toLowerCase() ===
                        normalizedTag
                    );

                }
            );

        if (exactVoice) {
            return exactVoice;
        }

        const languageVoice =
            availableVoices.find(
                function (voice) {

                    return voice.lang
                        .toLowerCase()
                        .startsWith(
                            languagePrefix
                        );

                }
            );

        if (languageVoice) {
            return languageVoice;
        }

        return (
            availableVoices.find(
                function (voice) {

                    return voice.lang
                        .toLowerCase()
                        .startsWith("en");

                }
            ) ||
            null
        );

    }

    function splitSpeechText(text) {

        const cleanText =
            String(text || "")
                .replace(/\s+/g, " ")
                .trim();

        if (!cleanText) {
            return [];
        }

        const parts =
            cleanText.match(
                /[^.!?।॥\n]+[.!?।॥]?/g
            ) || [cleanText];

        const chunks = [];

        let currentChunk = "";

        parts.forEach(function (part) {

            const nextChunk =
                currentChunk
                    ? currentChunk + " " + part.trim()
                    : part.trim();

            if (
                nextChunk.length > 220 &&
                currentChunk
            ) {

                chunks.push(
                    currentChunk.trim()
                );

                currentChunk =
                    part.trim();

            } else {

                currentChunk =
                    nextChunk;

            }

        });

        if (currentChunk) {

            chunks.push(
                currentChunk.trim()
            );

        }

        return chunks;
    }


    async function speakText(
        text,
        liveTextElement
    ) {

        if (
            !voiceReplyEnabled ||
            !text
        ) {

            if (liveTextElement) {
                liveTextElement.textContent =
                    String(text || "");
            }

            resetAssistantVisuals();

            return;
        }

        if (!audioPlayer) {

            throw new Error(
                "AI audio player not found."
            );

        }

        const fullText =
            String(text || "").trim();

        if (!fullText) {
            return;
        }

        audioPlayer.pause();

        audioPlayer.removeAttribute(
            "src"
        );

        audioPlayer.load();

        if (currentTtsController) {

            currentTtsController.abort();

        }

        currentTtsController =
            new AbortController();

        const response =
            await fetch(
                "/api/tts",
                {
                    method: "POST",

                    signal:
                        currentTtsController.signal,

                    credentials:
                        "same-origin",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "Accept":
                            "audio/mpeg"
                    },

                    body:
                        JSON.stringify({
                            text:
                                fullText,

                            languageCode:
                                userLanguageCode
                        })
                }
            );

        if (!response.ok) {

            let errorMessage =
                "Unable to generate voice.";

            try {

                const errorData =
                    await response.json();

                errorMessage =
                    errorData.error ||
                    errorMessage;

            } catch (error) {
                // Audio error response may not be JSON.
            }

            throw new Error(
                errorMessage
            );
        }

        const audioBlob =
            await response.blob();

        currentTtsController = null;


        /*
        * Speaker TTS request madhyalo OFF chesina
        * audio start kakunda stop chestundi.
        */
        if (!voiceReplyEnabled) {

            if (liveTextElement) {

                liveTextElement.textContent =
                    fullText;

            }

            resetAssistantVisuals();

            voiceStatus.textContent =
                "Voice is off";

            return;

        }


        const audioUrl =
            URL.createObjectURL(
                audioBlob
            );

        audioPlayer.src =
            audioUrl;

        setAvatarState(
            "speaking"
        );

        characterSection.classList.add(
            "is-speaking"
        );

        status.textContent =
            "Laxmi is speaking...";

        voiceStatus.textContent =
            "Laxmi is speaking...";

        if (liveTextElement) {

            liveTextElement.textContent =
                "";

        }

        await new Promise(
            function (
                resolve,
                reject
            ) {

                let wordTimer = null;

                currentSpeechCancel =
                    function () {

                        if (wordTimer) {

                            window.clearInterval(
                                wordTimer
                            );

                            wordTimer = null;

                        }

                        if (liveTextElement) {

                            liveTextElement.textContent =
                                fullText;

                        }

                        resolve();

                    };

                function startTextSync() {

                    if (!liveTextElement) {
                        return;
                    }

                    const words =
                        fullText.split(
                            /\s+/
                        );

                    let wordIndex = 0;

                    const audioDuration =
                        Number(
                            audioPlayer.duration
                        );

                    const totalDuration =
                        Number.isFinite(
                            audioDuration
                        ) &&
                        audioDuration > 0

                            ? audioDuration * 1000

                            : Math.max(
                                words.length * 430,
                                1500
                            );

                    const interval =
                        Math.max(
                            120,
                            totalDuration /
                            Math.max(
                                words.length,
                                1
                            )
                        );

                    wordTimer =
                        window.setInterval(
                            function () {

                                if (
                                    wordIndex >=
                                    words.length
                                ) {

                                    window.clearInterval(
                                        wordTimer
                                    );

                                    wordTimer = null;

                                    liveTextElement.textContent =
                                        fullText;

                                    return;

                                }

                                liveTextElement.textContent +=
                                    (
                                        wordIndex === 0
                                            ? ""
                                            : " "
                                    ) +
                                    words[wordIndex];

                                wordIndex++;

                                scrollMessagesToBottom();

                            },
                            interval
                        );

                }


                audioPlayer.onloadedmetadata =
                    function () {

                        startTextSync();

                    };


                audioPlayer.onended =
                    function () {

                        if (wordTimer) {

                            window.clearInterval(
                                wordTimer
                            );

                        }

                        if (liveTextElement) {

                            liveTextElement.textContent =
                                fullText;

                        }

                        URL.revokeObjectURL(
                            audioUrl
                        );

                        characterSection.classList.remove(
                            "is-speaking"
                        );

                        resetAssistantVisuals();

                        voiceStatus.textContent =
                            "Type or tap microphone";

                        currentSpeechCancel = null; 
                        
                        isSpeaking = false;

                        resolve();

                    };


                audioPlayer.onerror =
                    function () {

                        if (wordTimer) {

                            window.clearInterval(
                                wordTimer
                            );

                        }

                        URL.revokeObjectURL(
                            audioUrl
                        );

                        characterSection.classList.remove(
                            "is-speaking"
                        );

                        resetAssistantVisuals();

                        currentSpeechCancel = null;

                        reject(
                            new Error(
                                "Laxmi audio playback failed."
                            )
                        );

                    };

                    audioPlayer.play()
                    .then(function () {

                        isSpeaking = true;

                    })
                    .catch(
                    function (error) {

                        URL.revokeObjectURL(
                            audioUrl
                        );

                        reject(
                            error
                        );

                    }
                );

            }
        );

    }


    /* =====================================================
       GREETING
    ===================================================== */

    async function typeGreeting(text) {

        const currentRunId =
            ++greetingRunId;

        introBubble.textContent = "";

        const greetingText =
            String(text || "");

        for (
            const letter of greetingText
        ) {

            if (
                currentRunId !==
                greetingRunId
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

            status.textContent =
                "Welcoming you...";

            await wait(1050);

            introBubble.textContent =
                "";

            status.textContent =
                "Laxmi is speaking...";

            voiceStatus.textContent =
                "Please listen...";

            introBubble.textContent =
                "";

            const shortGreeting =
                String(
                    data.greeting || ""
                )
                    .split(/\r?\n/)
                    .map(function (line) {
                        return line.trim();
                    })
                    .find(Boolean)
                ||
                (
                    "Welcome, " +
                    (
                        data.name ||
                        "User"
                    )
                );

            await speakText(
                shortGreeting,
                introBubble
            );

            status.textContent =
                "Ready";

            voiceStatus.textContent =
                "Tap microphone or type your question";

        } catch (error) {

            console.log(
                "Greeting error:",
                error
            );

            const fallbackGreeting =
                "Hi 👋 I am Laxmi, your Basha AI Assistant. How can I help you?";

            await typeGreeting(
                fallbackGreeting
            );

            showError(
                error.message
            );

            resetAssistantVisuals();

        }

    }


    /* =====================================================
       OPEN FLY ANIMATION
    ===================================================== */

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
                        ? 20
                        : 46
                ),

            top:
                sectionRect.bottom -
                size -
                (
                    isMobile
                        ? 28
                        : 42
                ),

            width: size,

            height: size

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


    function resetFlyingAvatarStyles() {

        flyingAvatar.style.transform = "";

        flyingAvatar.style.opacity = "";

    }


    async function animateOpen() {

        if (
            isAnimating ||
            !shell.hidden
        ) {
            return;
        }

        isAnimating = true;

        primeSpeechSynthesis();

        hideError();

        stopListening();

        resetFlyingAvatarStyles();

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

        document.body.classList.add(
            "basha-ai-open"
        );

        await wait(110);

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
                typeof flyingAvatar.animate ===
                "function"
            ) {

                const animation =
                    flyingAvatar.animate(
                        [
                            {
                                transform:
                                    "translate3d(0, 0, 0) scale(1)",

                                opacity: 1
                            },

                            {
                                transform:
                                    "translate3d(" +
                                    (deltaX * 0.52) +
                                    "px, " +
                                    (deltaY * 0.24) +
                                    "px, 0) " +
                                    "scale(1.30) rotate(-7deg)",

                                opacity: 1,

                                offset: 0.45
                            },

                            {
                                transform:
                                    "translate3d(" +
                                    deltaX +
                                    "px, " +
                                    deltaY +
                                    "px, 0) " +
                                    "scale(" +
                                    scaleX +
                                    ", " +
                                    scaleY +
                                    ") rotate(0deg)",

                                opacity: 1
                            }
                        ],

                        {
                            duration: 760,

                            easing:
                                "cubic-bezier(.18,.84,.32,1)",

                            fill:
                                "forwards"
                        }
                    );

                await animation.finished;

            } else {

                await wait(400);

            }

        } catch (error) {

            console.log(
                "AI open animation error:",
                error
            );

        }

        flyingAvatar.hidden = true;

        resetFlyingAvatarStyles();

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

                if (
                    window.innerWidth >
                    600
                ) {

                    input.focus();

                }

            },
            150
        );

        if (!hasWelcomed) {

            hasWelcomed = true;

            initialized = true;

            await loadGreeting();

        } else {

            introBubble.classList.remove(
                "show"
            );

            status.textContent =
                "Online";

            voiceStatus.textContent =
                "Type or tap microphone";

            isSending = false;

            micButton.disabled = false;

            setupSpeechRecognition();

            updateCharacterCount();

        }

    }


    /* =====================================================
       REVERSE CLOSE ANIMATION
    ===================================================== */

    async function animateClose() {

        if (
            isAnimating ||
            shell.hidden
        ) {
            return;
        }

        isAnimating = true;

        greetingRunId++;

        stopCurrentAssistantActivity();

        stopAvatarAnimation();

        if (blinkTimer) {

            window.clearTimeout(
                blinkTimer
            );

        }        

        const characterRect =
            character.getBoundingClientRect();

        const startSize =
            Math.min(
                characterRect.width,
                characterRect.height,
                108
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

            width: startSize,

            height: startSize

        };

        const destination =
            topAvatar
                .getBoundingClientRect();

        setFlyingAvatarRect(
            startRect
        );

        const flyingImage =
            flyingAvatar.querySelector(
                "img"
            );

        if (flyingImage) {

            flyingImage.src =
                character.src ||
                avatarFrames.idle[0];

        }

        flyingAvatar.hidden = false;

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
                typeof flyingAvatar.animate ===
                "function"
            ) {

                const animation =
                    flyingAvatar.animate(
                        [
                            {
                                transform:
                                    "translate3d(0,0,0) scale(1)",

                                opacity: 1
                            },

                            {
                                transform:
                                    "translate3d(" +
                                    (deltaX * 0.55) +
                                    "px, " +
                                    (deltaY * 0.72) +
                                    "px, 0) " +
                                    "scale(.82) rotate(7deg)",

                                opacity: 1,

                                offset: 0.55
                            },

                            {
                                transform:
                                    "translate3d(" +
                                    deltaX +
                                    "px, " +
                                    deltaY +
                                    "px, 0) " +
                                    "scale(" +
                                    scaleX +
                                    ", " +
                                    scaleY +
                                    ") rotate(0deg)",

                                opacity: 0.96
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

                await animation.finished;

            } else {

                await wait(300);

            }

        } catch (error) {

            console.log(
                "AI close animation error:",
                error
            );

        }

        flyingAvatar.hidden = true;

        resetFlyingAvatarStyles();

        shell.hidden = true;

        openButton.classList.remove(
            "is-hidden"
        );

        document.body.classList.remove(
            "basha-ai-open"
        );

        /*
        * Backdrop మరియు GPU compositing cleanup.
        */
        if (backdrop) {

            backdrop.style.backdropFilter =
                "";

            backdrop.style.webkitBackdropFilter =
                "";

            backdrop.style.opacity =
                "";

            backdrop.style.transform =
                "";

        }

        shell.style.transform = "";
        shell.style.opacity = "";

        document.body.style.transform =
            "translateZ(0)";

        window.requestAnimationFrame(
            function () {

                document.body.style.transform =
                    "";

            }
        );

        resetAssistantVisuals();

        isAnimating = false;

    }


    /* =====================================================
       CLEAR CONVERSATION
    ===================================================== */

    function clearConversation() {

        stopCurrentAssistantActivity();

        conversationHistory = [];

        messages.innerHTML = "";

        input.value = "";

        introBubble.textContent = "";

        introBubble.classList.remove(
            "show"
        );

        resizeInput();

        hideError();

        thinking.hidden = true;

        isSending = false;

        micButton.disabled = false;

        status.textContent =
            "Online";

        voiceStatus.textContent =
            "Type or tap microphone";

        setupSpeechRecognition();

        updateCharacterCount();

    }


    /* =====================================================
       SEND MESSAGE
    ===================================================== */

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
            "Laxmi is thinking...";

        voiceStatus.textContent =
            "Preparing answer...";

        setAvatarState(
            "thinking"
        );

        scrollMessagesToBottom();

        try {

            /*
            * User message కనిపించిన తర్వాత
            * 3 seconds wait చేసి request పంపుతుంది.
            */
            await wait(
                AI_REPLY_DELAY
            );

            /*
            * ఈ 3 secondsలో panel close చేసినా
            * లేదా request cancel చేసినా API call పంపదు.
            */
            if (
                !isSending ||
                shell.hidden
            ) {
                return;
            }

            const historyForRequest =
                conversationHistory.slice(
                    0,
                    -1
                );

            if (currentChatController) {

                currentChatController.abort();

            }

            currentChatController =
                new AbortController();    

            const response =
                await fetch(
                    "/api/ai-assistant/chat",
                    {
                        method:
                            "POST",

                        signal:
                            currentChatController.signal,    

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

            currentChatController = null;    

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

            setupSpeechRecognition();

            thinking.hidden = true;

            status.textContent =
                "Laxmi is speaking...";

            voiceStatus.textContent =
                "Please listen...";

            const assistantContent =
                createMessage(
                    "assistant",
                    data.reply
                );

            await speakText(
                data.reply,
                assistantContent
            );

        } catch (error) {

            if (
                error &&
                error.name ===
                "AbortError"
            ) {

                console.log(
                    "AI request cancelled."
                );

                return;

            }

            console.log(
                "AI chat error:",
                error
            );

            showError(
                error.message ||
                "Unable to get AI response."
            );

            resetAssistantVisuals();

        } finally {

            isSending = false;

            thinking.hidden = true;

            micButton.disabled = false;

            currentChatController = null;

            currentTtsController = null;

            voiceStatus.textContent =
                "Type or tap microphone";

            if (
                !character.classList.contains(
                    "is-speaking"
                )
            ) {

                resetAssistantVisuals();

            }

            clearVoiceSilenceTimer();
            accumulatedVoiceText = "";
            lastFinalTranscript = "";
            updateCharacterCount();

        }

    }

    function clearVoiceSilenceTimer() {

        if (voiceSilenceTimer) {

            window.clearTimeout(
                voiceSilenceTimer
            );

            voiceSilenceTimer = null;

        }

    }


    function scheduleVoiceMessageSend() {

        clearVoiceSilenceTimer();

        if (
            !accumulatedVoiceText.trim()
        ) {
            return;
        }

        voiceStatus.textContent =
            "Waiting for more speech...";

        voiceSilenceTimer =
            window.setTimeout(
                function () {

                    const finalVoiceText =
                        accumulatedVoiceText.trim();

                    accumulatedVoiceText = "";

                    recognitionShouldRestart = false;

                    voiceSilenceTimer = null;

                    if (!finalVoiceText) {
                        return;
                    }

                    input.value =
                        finalVoiceText;

                    resizeInput();

                    updateCharacterCount();

                    stopListening(true);

                    voiceStatus.textContent =
                        "Sending voice message...";

                    sendMessage();

                },
                VOICE_SILENCE_DELAY
            );

    }

    /* =====================================================
    IPHONE / SAFARI MEDIA RECORDER
    ===================================================== */

    async function transcribeIOSAudio(
        audioBlob
    ) {

        if (
            !audioBlob ||
            audioBlob.size === 0
        ) {

            throw new Error(
                "Recorded audio is empty."
            );

        }

        if (iosTranscriptionController) {

            iosTranscriptionController.abort();

        }

        iosTranscriptionController =
            new AbortController();

        const mimeType =
            audioBlob.type ||
            "audio/mp4";

        const extension =
            getAudioFileExtension(
                mimeType
            );

        const formData =
            new FormData();

        formData.append(
            "audio",
            audioBlob,
            "laxmi-voice." + extension
        );

        formData.append(
            "languageCode",
            userLanguageCode || "en"
        );

        const response =
            await fetch(
                "/api/ai-assistant/transcribe",
                {
                    method: "POST",

                    signal:
                        iosTranscriptionController.signal,

                    credentials:
                        "same-origin",

                    body:
                        formData
                }
            );

        iosTranscriptionController = null;

        let data = null;

        try {

            data =
                await response.json();

        } catch (error) {

            data = {};

        }

        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.error ||
                "Unable to convert voice to text."
            );

        }

        const transcript =
            String(
                data.transcript ||
                data.text ||
                ""
            )
                .replace(/\s+/g, " ")
                .trim();

        if (!transcript) {

            throw new Error(
                "No speech was detected."
            );

        }

        return transcript;

    }


    async function finishIOSRecording(
        shouldSend
    ) {

        if (!iosMediaRecorder) {

            updateIOSMicUI(
                false
            );

            releaseIOSMediaStream();

            return;

        }

        clearIOSRecordingTimers();

        const recorder =
            iosMediaRecorder;

        iosMediaRecorder = null;

        const recordingDuration =
            Date.now() -
            iosRecordingStartedAt;

        iosRecordingStartedAt = 0;

        updateIOSMicUI(
            false
        );

        status.textContent =
            "Processing voice...";

        voiceStatus.textContent =
            "Converting voice to text...";

        const audioBlob =
            await new Promise(
                function (
                    resolve,
                    reject
                ) {

                    recorder.onstop =
                        function () {

                            try {

                                const blob =
                                    new Blob(
                                        iosAudioChunks,
                                        {
                                            type:
                                                recorder.mimeType ||
                                                "audio/mp4"
                                        }
                                    );

                                iosAudioChunks = [];

                                resolve(
                                    blob
                                );

                            } catch (error) {

                                reject(
                                    error
                                );

                            }

                        };

                    recorder.onerror =
                        function (event) {

                            reject(
                                event.error ||
                                new Error(
                                    "Voice recording failed."
                                )
                            );

                        };

                    try {

                        if (
                            recorder.state !==
                            "inactive"
                        ) {

                            recorder.stop();

                        } else {

                            const blob =
                                new Blob(
                                    iosAudioChunks,
                                    {
                                        type:
                                            recorder.mimeType ||
                                            "audio/mp4"
                                    }
                                );

                            iosAudioChunks = [];

                            resolve(
                                blob
                            );

                        }

                    } catch (error) {

                        reject(
                            error
                        );

                    }

                }
            );

        releaseIOSMediaStream();

        if (!shouldSend) {

            status.textContent =
                "Online";

            voiceStatus.textContent =
                "Type or tap microphone";

            return;

        }

        if (
            recordingDuration <
            500
        ) {

            status.textContent =
                "Online";

            voiceStatus.textContent =
                "Please speak for a little longer";

            return;

        }

        try {

            const transcript =
                await transcribeIOSAudio(
                    audioBlob
                );

            input.value =
                transcript;

            resizeInput();

            updateCharacterCount();

            status.textContent =
                "Voice received";

            voiceStatus.textContent =
                "Sending voice message...";

            await wait(
                250
            );

            await sendMessage();

        } catch (error) {

            if (
                error &&
                error.name ===
                "AbortError"
            ) {

                return;

            }

            console.log(
                "iPhone transcription error:",
                error
            );

            status.textContent =
                "Online";

            voiceStatus.textContent =
                "Type or tap microphone";

            showError(
                error.message ||
                "Unable to process voice."
            );

        }

    }


    async function startIOSRecording() {

        if (isSending) {
            return;
        }

        if (!supportsMediaRecorder()) {

            showError(
                "Voice recording is not supported in this iPhone browser. Please update iOS or use Safari."
            );

            return;

        }

        hideError();

        /*
        * Stop Laxmi audio only.
        * Do not reset iPhone recorder state here.
        */
        if (currentTtsController) {

            currentTtsController.abort();

            currentTtsController = null;

        }

        if (currentSpeechCancel) {

            currentSpeechCancel();

            currentSpeechCancel = null;

        }

        if (audioPlayer) {

            audioPlayer.pause();

            audioPlayer.currentTime = 0;

            audioPlayer.removeAttribute(
                "src"
            );

            audioPlayer.load();

        }

        stopSpeechKeepAlive();

        if (
            "speechSynthesis"
            in window
        ) {

            window.speechSynthesis.cancel();

        }

        isSpeaking = false;

        characterSection.classList.remove(
            "is-speaking"
        );

        iosAudioChunks = [];

        try {

            iosMediaStream =
                await navigator
                    .mediaDevices
                    .getUserMedia({
                        audio: {
                            echoCancellation: true,
                            noiseSuppression: true,
                            autoGainControl: true
                        }
                    });

            const mimeType =
                getSupportedAudioMimeType();

            const recorderOptions =
                mimeType
                    ? {
                        mimeType:
                            mimeType
                    }
                    : undefined;

            iosMediaRecorder =
                recorderOptions
                    ? new MediaRecorder(
                        iosMediaStream,
                        recorderOptions
                    )
                    : new MediaRecorder(
                        iosMediaStream
                    );

            iosMediaRecorder.ondataavailable =
                function (event) {

                    if (
                        event.data &&
                        event.data.size > 0
                    ) {

                        iosAudioChunks.push(
                            event.data
                        );

                    }

                };

            iosMediaRecorder.onerror =
                function (event) {

                    console.log(
                        "iPhone recorder error:",
                        event.error ||
                        event
                    );

                    clearIOSRecordingTimers();

                    updateIOSMicUI(
                        false
                    );

                    releaseIOSMediaStream();

                    status.textContent =
                        "Online";

                    voiceStatus.textContent =
                        "Voice recording failed";

                    showError(
                        "Unable to record voice on this iPhone."
                    );

                };

            iosRecordingStartedAt =
                Date.now();

            iosMediaRecorder.start(
                250
            );

            updateIOSMicUI(
                true
            );

            status.textContent =
                "Laxmi is listening...";

            voiceStatus.textContent =
                "Speak now. Tap stop when finished.";

            /*
            * iPhone MediaRecorder browser levelలో
            * reliable silence detection ఇవ్వదు.
            * User మాట్లాడడం పూర్తయ్యాక stop button press చేయవచ్చు.
            *
            * ఈ timer safety maximum మాత్రమే.
            */
            iosMaximumTimer =
                window.setTimeout(
                    function () {

                        if (iosIsRecording) {

                            finishIOSRecording(
                                true
                            );

                        }

                    },
                    IOS_MAXIMUM_RECORDING_TIME
                );

        } catch (error) {

            console.log(
                "iPhone microphone start error:",
                error
            );

            clearIOSRecordingTimers();

            updateIOSMicUI(
                false
            );

            releaseIOSMediaStream();

            status.textContent =
                "Online";

            voiceStatus.textContent =
                "Microphone permission required";

            if (
                error &&
                (
                    error.name ===
                        "NotAllowedError" ||
                    error.name ===
                        "PermissionDeniedError"
                )
            ) {

                showError(
                    "Please allow microphone permission in iPhone Safari Website Settings."
                );

                return;

            }

            if (
                error &&
                error.name ===
                    "NotFoundError"
            ) {

                showError(
                    "No microphone was found on this device."
                );

                return;

            }

            showError(
                error.message ||
                "Unable to start microphone."
            );

        }

    }


    async function toggleIOSRecording() {

        if (iosIsRecording) {

            await finishIOSRecording(
                true
            );

            return;

        }

        await startIOSRecording();

    }


    /* =====================================================
       SPEECH RECOGNITION
    ===================================================== */

    function setupSpeechRecognition() {

        /*
        * IMPORTANT:
        * iPhone check must come before SpeechRecognition check.
        *
        * iPhone Safari uses MediaRecorder.
        * Chrome/Android/Desktop use SpeechRecognition.
        */
        if (isIOSDevice()) {

            recognition = null;

            const mediaRecorderSupported =
                supportsMediaRecorder();

            micButton.disabled =
                !mediaRecorderSupported;

            micButton.classList.remove(
                "is-listening"
            );

            micButton.innerHTML =
                '<i class="bi bi-mic-fill"></i>';

            voiceStatus.textContent =
                mediaRecorderSupported
                    ? "Tap microphone to record"
                    : "Voice recording is not supported";

            return;
        }


        const SpeechRecognition =
            window.SpeechRecognition ||
            window.webkitSpeechRecognition;


        if (!SpeechRecognition) {

            recognition = null;

            micButton.disabled = true;

            micButton.classList.remove(
                "is-listening"
            );

            micButton.innerHTML =
                '<i class="bi bi-mic-fill"></i>';

            voiceStatus.textContent =
                "Voice input is not supported in this browser";

            return;
        }


        micButton.disabled = false;


        if (recognition) {

            recognition.lang =
                speechLanguageMap[
                    userLanguageCode
                ] ||
                userLanguageCode ||
                "en-IN";

            return;
        }


        recognition =
            new SpeechRecognition();


        recognition.continuous = true;

        recognition.interimResults = true;

        recognition.maxAlternatives = 1;

        recognition.lang =
            speechLanguageMap[
                userLanguageCode
            ] ||
            userLanguageCode ||
            "en-IN";


        recognition.onstart =
            function () {

                isListening = true;

                recognitionShouldRestart = true;

                micButton.disabled = false;

                micButton.classList.add(
                    "is-listening"
                );

                micButton.innerHTML =
                    '<i class="bi bi-stop-fill"></i>';

                voiceStatus.textContent =
                    "Listening...";

                status.textContent =
                    "Laxmi is listening...";

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
                        String(
                            event.results[
                                index
                            ][0].transcript || ""
                        )
                            .replace(/\s+/g, " ")
                            .trim();


                    if (!transcript) {
                        continue;
                    }


                    if (
                        event.results[
                            index
                        ].isFinal
                    ) {

                        finalText +=
                            (
                                finalText
                                    ? " "
                                    : ""
                            ) +
                            transcript;

                    } else {

                        interimText +=
                            (
                                interimText
                                    ? " "
                                    : ""
                            ) +
                            transcript;

                    }

                }


                if (finalText) {

                    const normalizedFinalText =
                        finalText
                            .replace(/\s+/g, " ")
                            .trim();


                    if (
                        normalizedFinalText &&
                        normalizedFinalText !==
                            lastFinalTranscript
                    ) {

                        const oldWords =
                            accumulatedVoiceText
                                .split(/\s+/)
                                .filter(Boolean);

                        const newWords =
                            normalizedFinalText
                                .split(/\s+/)
                                .filter(Boolean);


                        const oldTail =
                            oldWords
                                .slice(
                                    -newWords.length
                                )
                                .join(" ")
                                .toLowerCase();

                        const newTextLower =
                            newWords
                                .join(" ")
                                .toLowerCase();


                        if (
                            oldTail !==
                            newTextLower
                        ) {

                            accumulatedVoiceText =
                                (
                                    accumulatedVoiceText +
                                    " " +
                                    normalizedFinalText
                                )
                                    .replace(
                                        /\s+/g,
                                        " "
                                    )
                                    .trim();

                        }

                        lastFinalTranscript =
                            normalizedFinalText;

                    }

                    scheduleVoiceMessageSend();

                }


                if (interimText) {

                    clearVoiceSilenceTimer();

                }


                const visibleText =
                    (
                        accumulatedVoiceText +
                        " " +
                        interimText
                    )
                        .replace(
                            /\s+/g,
                            " "
                        )
                        .trim();


                input.value =
                    visibleText;

                resizeInput();

                updateCharacterCount();


                if (interimText) {

                    voiceStatus.textContent =
                        "Listening...";

                    status.textContent =
                        "Laxmi is listening...";

                } else if (
                    accumulatedVoiceText
                ) {

                    voiceStatus.textContent =
                        "Waiting 3 seconds...";

                }

            };


        recognition.onerror =
            function (event) {

                console.log(
                    "Voice recognition error:",
                    event.error
                );


                if (
                    event.error ===
                        "not-allowed" ||
                    event.error ===
                        "service-not-allowed"
                ) {

                    recognitionShouldRestart =
                        false;

                    stopListening();

                    showError(
                        "Please allow microphone permission in browser settings."
                    );

                    return;

                }


                if (
                    event.error ===
                        "no-speech" &&
                    recognitionShouldRestart
                ) {

                    return;

                }


                if (
                    event.error ===
                        "aborted"
                ) {

                    return;

                }


                recognitionShouldRestart =
                    false;

                stopListening();

                showError(
                    "Voice input error: " +
                    event.error
                );

            };


        recognition.onend =
            function () {

                if (
                    isListening &&
                    recognitionShouldRestart &&
                    !isSending
                ) {

                    window.setTimeout(
                        function () {

                            if (
                                !isListening ||
                                !recognitionShouldRestart ||
                                isSending ||
                                !recognition
                            ) {
                                return;
                            }

                            try {

                                recognition.start();

                            } catch (error) {

                                console.log(
                                    "Voice recognition restart:",
                                    error
                                );

                            }

                        },
                        500
                    );

                    return;

                }


                micButton.classList.remove(
                    "is-listening"
                );

                micButton.innerHTML =
                    '<i class="bi bi-mic-fill"></i>';


                if (!isSending) {

                    status.textContent =
                        "Online";

                }

            };

    }

    function startListening() {

        if (isSending) {
            return;
        }

        if (isIOSDevice()) {

            toggleIOSRecording();

            return;

        }

        /*
        * Stop only Laxmi voice playback.
        * Do not reset the microphone recognition object here.
        */
        if (currentTtsController) {

            currentTtsController.abort();

            currentTtsController = null;

        }

        if (currentSpeechCancel) {

            currentSpeechCancel();

            currentSpeechCancel = null;

        }

        if (audioPlayer) {

            audioPlayer.pause();

            audioPlayer.currentTime = 0;

            audioPlayer.removeAttribute(
                "src"
            );

            audioPlayer.load();

        }

        stopSpeechKeepAlive();

        if (
            "speechSynthesis"
            in window
        ) {

            window.speechSynthesis.cancel();

        }

        isSpeaking = false;

        characterSection.classList.remove(
            "is-speaking"
        );

        clearVoiceSilenceTimer();

        accumulatedVoiceText = "";

        recognitionShouldRestart = true;

        if (!recognition) {

            setupSpeechRecognition();

        }

        if (!recognition) {
            return;
        }

        hideError();

        /*
        * Laxmi voice play అవుతుంటే
        * microphone start చేసినప్పుడు stop చేయాలి.
        */
        if (audioPlayer) {

            audioPlayer.pause();

            audioPlayer.currentTime = 0;

        }

        stopSpeechKeepAlive();

        if (
            "speechSynthesis"
            in window
        ) {

            window.speechSynthesis.cancel();

        }

        input.value = "";

        resizeInput();

        updateCharacterCount();

        setAvatarState(
            "idle"
        );

        recognition.lang =
            speechLanguageMap[
                userLanguageCode
            ] ||
            userLanguageCode ||
            "en-IN";

        voiceStatus.textContent =
            "Listening...";

        status.textContent =
            "Laxmi is listening...";

        try {

            recognition.start();

        } catch (error) {

            console.log(
                "Speech recognition already active:",
                error
            );

        }

    }


    function stopListening(
        keepSilenceTimer
    ) {

        recognitionShouldRestart = false;

        /*
        * Silence timer నుంచే stopListening
        * call అయితే timerని మళ్లీ clear చేయాల్సిన
        * అవసరం లేదు.
        */
        if (!keepSilenceTimer) {

            clearVoiceSilenceTimer();

        }

        if (
            recognition &&
            isListening
        ) {

            try {

                recognition.stop();

            } catch (error) {

                console.log(
                    "Stop recognition error:",
                    error
                );

            }

        }

        isListening = false;

        micButton.classList.remove(
            "is-listening"
        );

        micButton.innerHTML =
            '<i class="bi bi-mic-fill"></i>';

        if (!isSending) {

            voiceStatus.textContent =
                "Type or tap microphone";

            status.textContent =
                "Online";

        }

    }


    /* =====================================================
       VOICE TOGGLE
    ===================================================== */

    function updateVoiceToggleUI() {

        voiceToggle.classList.toggle(
            "is-muted",
            !voiceReplyEnabled
        );

        voiceToggle.innerHTML =

            voiceReplyEnabled

                ? '<i class="bi bi-volume-up-fill"></i>'

                : '<i class="bi bi-volume-mute-fill"></i>';

        voiceToggle.setAttribute(
            "aria-pressed",
            voiceReplyEnabled
                ? "false"
                : "true"
        );

    }


    /* =====================================================
       EVENTS
    ===================================================== */

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

    /* ==========================================
    MOBILE KEYBOARD VIEWPORT EVENTS
    =========================================== */

    window.addEventListener(
        "resize",
        updateAiMobileViewport
    );

    window.addEventListener(
        "orientationchange",
        updateAiMobileViewport
    );

    if (window.visualViewport) {

        window.visualViewport.addEventListener(
            "resize",
            updateAiMobileViewport
        );

        window.visualViewport.addEventListener(
            "scroll",
            updateAiMobileViewport
        );

    }

    input.addEventListener(
        "focus",
        function () {

            window.setTimeout(
                updateAiMobileViewport,
                100
            );

        }
    );

    input.addEventListener(
        "blur",
        function () {

            window.setTimeout(
                updateAiMobileViewport,
                100
            );

        }
    );

    updateAiMobileViewport();


    voiceToggle.addEventListener(
        "click",
        function () {

            voiceReplyEnabled = !voiceReplyEnabled;

            localStorage.setItem(
                "bashaAiVoiceReply",
                voiceReplyEnabled ? "on" : "off"
            );

            if (!voiceReplyEnabled) {

                stopCurrentAssistantActivity();

                if (audioPlayer) {
                    audioPlayer.pause();
                    audioPlayer.currentTime = 0;
                }

                if (window.speechSynthesis) {
                    window.speechSynthesis.cancel();
                }

                status.textContent = "Voice Off";

            } else {

                status.textContent = "Online";

            }

            updateVoiceToggleUI();

            if (!voiceReplyEnabled) {

                stopSpeechKeepAlive();

                if (
                    "speechSynthesis"
                    in window
                ) {

                    window.speechSynthesis.cancel();

                }

                resetAssistantVisuals();

                voiceStatus.textContent =
                    "Voice reply is off";

            } else {

                primeSpeechSynthesis();

                voiceStatus.textContent =
                    "Voice reply is on";

            }

        }
    );


    micButton.addEventListener(
        "click",
        async function () {

            hideError();

            if (isIOSDevice()) {

                await toggleIOSRecording();

                return;

            }

            if (isListening) {

                const spokenText =
                    (
                        accumulatedVoiceText ||
                        input.value ||
                        ""
                    ).trim();

                recognitionShouldRestart =
                    false;

                clearVoiceSilenceTimer();

                stopListening();

                if (spokenText) {

                    accumulatedVoiceText =
                        "";

                    lastFinalTranscript =
                        "";

                    input.value =
                        spokenText;

                    resizeInput();

                    updateCharacterCount();

                    voiceStatus.textContent =
                        "Sending voice message...";

                    await sendMessage();

                }

                return;

            }

            if (isSpeaking) {

                stopCurrentAssistantActivity();

            }

            startListening();

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


    document.addEventListener(
        "visibilitychange",
        function () {

            pageIsVisible =
                document.visibilityState ===
                "visible";

            if (!pageIsVisible) {

                stopCurrentAssistantActivity();

                if (audioPlayer) {

                    audioPlayer.pause();

                    audioPlayer.currentTime = 0;

                }

                if (blinkTimer) {

                    window.clearTimeout(blinkTimer);

                }

                return;

            } else if (!shell.hidden) {

                if (
                    avatarState !==
                    "speaking" &&
                    avatarState !==
                    "thinking"
                ) {

                    setAvatarState(
                        "idle"
                    );

                }

                scheduleBlink();

            }

        }
    );

    window.addEventListener(
        "pagehide",
        function () {

            stopCurrentAssistantActivity();
            
            if (audioPlayer) {

                audioPlayer.pause();

                audioPlayer.currentTime = 0;

            }

        }
    );

    window.addEventListener(
        "blur",
        function () {

            stopCurrentAssistantActivity();

            if (audioPlayer) {

                audioPlayer.pause();

                audioPlayer.currentTime = 0;

            }

        }
    );

    window.addEventListener(
        "beforeunload",
        function () {

            stopCurrentAssistantActivity();

            if (audioPlayer) {

                audioPlayer.pause();

                audioPlayer.currentTime = 0;

            }

            stopAvatarAnimation();

        }
    );

    /* =====================================================
       SPEECH VOICES LOAD
    ===================================================== */

    if (
        "speechSynthesis"
        in window
    ) {

        window.speechSynthesis.onvoiceschanged =
            function () {

                window.speechSynthesis.getVoices();

            };

    }

    /* =====================================================
       INITIAL SETUP
    ===================================================== */

    installImageFallbacks();

    preloadAvatarImages();

    setHeaderAvatarFrame(
        avatarFrames.idle[0] ||
        avatarFrames.fallback
    );

    if (thinkingAvatar) {

        thinkingAvatar.src =
            avatarFrames.thinking[0] ||
            avatarFrames.fallback;

    }

    setMainAvatarFrame(
        avatarFrames.idle[0] ||
        avatarFrames.fallback
    );

    setAvatarState(
        "idle"
    );

    updateVoiceToggleUI();

    setupSpeechRecognition();

    updateCharacterCount();        

});