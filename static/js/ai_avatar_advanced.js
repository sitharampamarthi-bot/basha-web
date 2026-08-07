"use strict";

console.log("BASHA ADVANCED AI JS LOADED");

document.addEventListener("DOMContentLoaded", function () {
    function getElement(id) {
        return document.getElementById(id);
    }

    const openButton = getElement("bashaAiOpenButton");
    const topAvatar = getElement("bashaAiTopAvatar");
    const flyingAvatar = getElement("bashaAiFlyingAvatar");
    const shell = getElement("bashaAiShell");

    if (!openButton || !topAvatar || !flyingAvatar || !shell) {
        console.log("Basha AI required elements not found.");
        return;
    }

    const panel = getElement("bashaAiPanel");
    const backdrop = getElement("bashaAiBackdrop");
    const closeButton = getElement("bashaAiCloseButton");
    const clearButton = getElement("bashaAiClearButton");
    const voiceToggle = getElement("bashaAiVoiceToggle");
    const stopSpeakingButton = getElement("bashaAiStopSpeakingButton");
    const character = getElement("bashaAiCharacter");
    const headerAvatar = getElement("bashaAiHeaderAvatar");
    const thinkingAvatar = getElement("bashaAiThinkingAvatar");
    const characterSection = getElement("bashaAiCharacterSection");
    const introBubble = getElement("bashaAiIntroBubble");
    const messages = getElement("bashaAiMessages");
    const thinking = getElement("bashaAiThinking");
    const errorBox = getElement("bashaAiError");
    const input = getElement("bashaAiInput");
    const micButton = getElement("bashaAiMicButton");
    const sendButton = getElement("bashaAiSendButton");
    const status = getElement("bashaAiStatus");
    const voiceStatus = getElement("bashaAiVoiceStatus");
    const characterCount = getElement("bashaAiCharacterCount");
    const audioPlayer = getElement("bashaAiAudioPlayer");

    const requiredElements = [
        panel,
        backdrop,
        closeButton,
        clearButton,
        voiceToggle,
        stopSpeakingButton,
        character,
        headerAvatar,
        thinkingAvatar,
        characterSection,
        introBubble,
        messages,
        thinking,
        errorBox,
        input,
        micButton,
        sendButton,
        status,
        voiceStatus,
        characterCount,
        audioPlayer,
    ];

    if (requiredElements.some(function (element) { return !element; })) {
        console.log("Basha AI widget is incomplete.");
        return;
    }

    const avatarFrames = {
        idle: [
            shell.dataset.idle1,
            shell.dataset.idle2,
            shell.dataset.idle3,
            shell.dataset.idle4,
        ].filter(Boolean),

        blink: [
            shell.dataset.blink1,
            shell.dataset.blink2,
        ].filter(Boolean),

        wave: [
            shell.dataset.wave1,
            shell.dataset.wave2,
            shell.dataset.wave3,
            shell.dataset.wave4,
            shell.dataset.wave5,
        ].filter(Boolean),

        thinking: [
            shell.dataset.thinking1,
            shell.dataset.thinking2,
            shell.dataset.thinking3,
            shell.dataset.thinking4,
            shell.dataset.thinking5,
        ].filter(Boolean),

        speaking: [
            shell.dataset.speaking1,
            shell.dataset.speaking2,
            shell.dataset.speaking3,
            shell.dataset.speaking4,
        ].filter(Boolean),

        explaining: [
            shell.dataset.explaining1,
            shell.dataset.explaining2,
            shell.dataset.explaining3,
            shell.dataset.explaining4,
            shell.dataset.explaining5,
        ].filter(Boolean),

        fallback:
            shell.dataset.fallbackSrc ||
            "/static/images/ai/idle-1.png",
    };

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
        zh: "zh-CN",
    };

    const SILENT_AUDIO_DATA_URI =
        "data:audio/wav;base64,UklGRqQCAABXQVZFZm10IBAAAAABAAEAQB8AAIA+AAACABAAZGF0YYACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA";

    const VOICE_SILENCE_DELAY = 3000;
    const AI_REPLY_DELAY = 250;
    const IOS_MAXIMUM_RECORDING_TIME = 60000;
    const TTS_MAX_CHUNK_BYTES = 3200;

    let hasWelcomed = false;
    let isSending = false;
    let isAnimating = false;
    let isListening = false;
    let isSpeaking = false;

    let pageIsVisible =
        document.visibilityState === "visible";

    let userLanguageCode = "en";

    let conversationHistory = [];

    let currentChatController = null;
    let currentTtsController = null;
    let iosTranscriptionController = null;

    let recognition = null;
    let recognitionShouldRestart = false;
    let recognitionSessionBaseText = "";
    let recognitionFinalSegments = new Map();

    let accumulatedVoiceText = "";
    let voiceSilenceTimer = null;

    let avatarAnimationTimer = null;
    let blinkTimer = null;
    let avatarState = "idle";
    let avatarFrameIndex = 0;

    let greetingRunId = 0;

    let speechRunId = 0;
    let currentSpeechCancel = null;
    let currentSpeechDisplay = null;
    let activeAudioObjectUrl = "";
    let pendingSpeech = null;

    let audioPlaybackUnlocked =
        !isIOSDevice();

    let audioUnlockPromise = null;

    let iosMediaRecorder = null;
    let iosMediaStream = null;
    let iosAudioChunks = [];
    let iosMaximumTimer = null;
    let iosRecordingStartedAt = 0;
    let iosIsRecording = false;
    let iosStopPromise = null;
    let iosVoiceRunId = 0;
    let iosActiveRunId = 0;

    let pageScrollY = 0;
    let viewportAnimationFrame = null;

    let voiceReplyEnabled =
        localStorage.getItem("bashaAiVoiceReply") !== "off";


    /* =====================================================
       GENERAL HELPERS
    ===================================================== */

    function wait(milliseconds) {
        return new Promise(function (resolve) {
            window.setTimeout(
                resolve,
                milliseconds
            );
        });
    }


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


    function getCurrentTime() {
        return new Intl.DateTimeFormat(
            [],
            {
                hour: "2-digit",
                minute: "2-digit",
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
        input.style.height = "auto";

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


    function lockPageScroll() {
        pageScrollY =
            window.scrollY ||
            window.pageYOffset ||
            0;

        document.body.style.top =
            "-" + pageScrollY + "px";

        document.body.classList.add(
            "basha-ai-open"
        );
    }


    function unlockPageScroll() {
        document.body.classList.remove(
            "basha-ai-open"
        );

        document.body.style.top = "";

        window.scrollTo(
            0,
            pageScrollY
        );
    }


    /* =====================================================
       MOBILE VIEWPORT / SAFARI KEYBOARD
    ===================================================== */

    function updateAiMobileViewport() {
        if (viewportAnimationFrame) {
            window.cancelAnimationFrame(
                viewportAnimationFrame
            );
        }

        viewportAnimationFrame =
            window.requestAnimationFrame(
                function () {
                    viewportAnimationFrame = null;

                    const viewport =
                        window.visualViewport;

                    const visibleHeight =
                        Math.max(
                            320,
                            Math.round(
                                viewport
                                    ? viewport.height
                                    : window.innerHeight
                            )
                        );

                    const viewportTop =
                        Math.max(
                            0,
                            Math.round(
                                viewport
                                    ? viewport.offsetTop
                                    : 0
                            )
                        );

                    const viewportLeft =
                        Math.max(
                            0,
                            Math.round(
                                viewport
                                    ? viewport.offsetLeft
                                    : 0
                            )
                        );

                    const layoutHeight =
                        Math.max(
                            document.documentElement.clientHeight,
                            window.innerHeight || 0
                        );

                    const keyboardHeight =
                        Math.max(
                            0,
                            layoutHeight -
                            visibleHeight -
                            viewportTop
                        );

                    document.documentElement.style.setProperty(
                        "--basha-ai-visible-height",
                        visibleHeight + "px"
                    );

                    document.documentElement.style.setProperty(
                        "--basha-ai-viewport-top",
                        viewportTop + "px"
                    );

                    document.documentElement.style.setProperty(
                        "--basha-ai-viewport-left",
                        viewportLeft + "px"
                    );

                    shell.classList.toggle(
                        "keyboard-open",
                        document.activeElement === input &&
                        keyboardHeight > 140
                    );

                    if (
                        document.activeElement === input
                    ) {
                        scrollMessagesToBottom();
                    }
                }
            );
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
        [
            ...avatarFrames.idle,
            ...avatarFrames.blink,
            ...avatarFrames.wave,
            ...avatarFrames.thinking,
            ...avatarFrames.speaking,
            ...avatarFrames.explaining,
        ].forEach(
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
        character.src =
            imageSource ||
            avatarFrames.fallback;
    }


    function setHeaderAvatarFrame(
        imageSource
    ) {
        headerAvatar.src =
            imageSource ||
            avatarFrames.fallback;
    }


    function stopAvatarAnimation() {
        if (avatarAnimationTimer) {
            window.clearInterval(
                avatarAnimationTimer
            );

            avatarAnimationTimer = null;
        }

        avatarFrameIndex = 0;
    }


    function removeAvatarClasses() {
        character.classList.remove(
            "is-idle",
            "is-speaking",
            "is-thinking",
            "is-explaining",
            "is-wave",
            "is-blinking",
            "is-blink"
        );
    }


    function playAvatarFrames(
        stateName,
        options
    ) {
        const settings =
            options || {};

        const frames =
            avatarFrames[stateName];

        if (
            !frames ||
            !frames.length
        ) {
            setMainAvatarFrame(
                avatarFrames.fallback
            );

            return;
        }

        stopAvatarAnimation();
        removeAvatarClasses();

        avatarState =
            stateName;

        avatarFrameIndex = 0;

        const speed =
            Number(settings.speed) ||
            250;

        const loop =
            settings.loop !== false;

        const returnToIdle =
            settings.returnToIdle !== false;

        character.classList.add(
            "is-" + stateName
        );

        setMainAvatarFrame(
            frames[0]
        );

        if (
            stateName === "thinking"
        ) {
            thinkingAvatar.src =
                frames[0];
        }

        avatarAnimationTimer =
            window.setInterval(
                function () {
                    if (
                        !pageIsVisible &&
                        stateName !== "speaking"
                    ) {
                        return;
                    }

                    avatarFrameIndex += 1;

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
                        stateName === "thinking"
                    ) {
                        thinkingAvatar.src =
                            frame;
                    }
                },
                speed
            );
    }


    function setAvatarState(
        stateName
    ) {
        const stateOptions = {
            idle: {
                speed: 620,
                loop: true,
                returnToIdle: false
            },

            blink: {
                speed: 115,
                loop: false,
                returnToIdle: true
            },

            wave: {
                speed: 220,
                loop: false,
                returnToIdle: true
            },

            thinking: {
                speed: 270,
                loop: true,
                returnToIdle: false
            },

            explaining: {
                speed: 230,
                loop: true,
                returnToIdle: false
            },

            speaking: {
                speed: 145,
                loop: true,
                returnToIdle: false
            },
        };

        playAvatarFrames(
            stateName,
            stateOptions[stateName] ||
            stateOptions.idle
        );
    }


    function resetAssistantVisuals() {
        setAvatarState(
            "idle"
        );

        status.textContent =
            "Online";
    }


    function scheduleBlink() {
        if (blinkTimer) {
            window.clearTimeout(
                blinkTimer
            );
        }

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
                3500 +
                Math.random() * 3500
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
            text: String(text || ""),
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

            return contentElement;
        }

        if (
            role === "assistant"
        ) {
            setAvatarState(
                "explaining"
            );

            status.textContent =
                "Laxmi is explaining...";
        }

        for (
            const letter of fullText
        ) {
            contentElement.textContent +=
                letter;

            scrollMessagesToBottom();

            await wait(11);
        }

        return contentElement;
    }


    /* =====================================================
       AUDIO / TTS
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


    function setStopSpeakingVisible(
        visible
    ) {
        const isVisible =
            Boolean(visible);

        stopSpeakingButton.hidden =
            !isVisible;

        stopSpeakingButton.disabled =
            !isVisible;

        stopSpeakingButton.classList.toggle(
            "is-active",
            isVisible
        );
    }


    function revokeActiveAudioUrl() {
        if (!activeAudioObjectUrl) {
            return;
        }

        URL.revokeObjectURL(
            activeAudioObjectUrl
        );

        activeAudioObjectUrl = "";
    }


    function resetAudioElement() {
        audioPlayer.pause();

        try {
            audioPlayer.currentTime = 0;
        } catch (error) {
            console.log(
                "Audio reset error:",
                error
            );
        }

        audioPlayer.onloadedmetadata = null;
        audioPlayer.onended = null;
        audioPlayer.onerror = null;

        audioPlayer.removeAttribute(
            "src"
        );

        audioPlayer.load();

        revokeActiveAudioUrl();
    }


    /* =====================================================
       IOS AUTOPLAY UNLOCK
    ===================================================== */

    async function unlockAudioPlayback() {
        if (!isIOSDevice()) {
            audioPlaybackUnlocked = true;
            return true;
        }

        if (audioPlaybackUnlocked) {
            return true;
        }

        if (audioUnlockPromise) {
            return audioUnlockPromise;
        }

        if (
            isSpeaking ||
            activeAudioObjectUrl
        ) {
            return false;
        }

        audioUnlockPromise =
            (
                async function () {
                    try {
                        audioPlayer.src =
                            SILENT_AUDIO_DATA_URI;

                        audioPlayer.volume = 1;

                        const playPromise =
                            audioPlayer.play();

                        if (
                            playPromise &&
                            typeof playPromise.then ===
                                "function"
                        ) {
                            await playPromise;
                        }

                        audioPlayer.pause();

                        audioPlayer.currentTime = 0;

                        audioPlayer.removeAttribute(
                            "src"
                        );

                        audioPlayer.load();

                        audioPlaybackUnlocked =
                            true;

                        return true;

                    } catch (error) {
                        console.log(
                            "iPhone audio unlock error:",
                            error
                        );

                        audioPlaybackUnlocked =
                            false;

                        return false;

                    } finally {
                        audioUnlockPromise =
                            null;
                    }
                }
            )();

        return audioUnlockPromise;
    }


    /* =====================================================
       STOP SPEECH ONLY
    ===================================================== */

    function stopAssistantSpeech(
        options
    ) {
        const settings =
            options || {};

        speechRunId += 1;

        if (currentTtsController) {
            currentTtsController.abort();
            currentTtsController = null;
        }

        if (currentSpeechCancel) {
            currentSpeechCancel();
            currentSpeechCancel = null;
        }

        if (
            currentSpeechDisplay &&
            currentSpeechDisplay.element
        ) {
            currentSpeechDisplay.element.textContent =
                currentSpeechDisplay.fullText;
        }

        currentSpeechDisplay = null;
        pendingSpeech = null;

        resetAudioElement();

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

        setStopSpeakingVisible(
            false
        );

        if (
            settings.resetVisuals !== false
        ) {
            resetAssistantVisuals();
        }

        if (
            !settings.keepVoiceStatus
        ) {
            voiceStatus.textContent =
                voiceReplyEnabled
                    ? "Type or tap microphone"
                    : "Voice reply is off";
        }
    }


    function utf8Length(
        value
    ) {
        return new TextEncoder()
            .encode(
                String(value || "")
            )
            .length;
    }


    /* =====================================================
       SPLIT LONG TTS
    ===================================================== */

    function splitSpeechText(
        text
    ) {
        const cleanText =
            String(text || "")
                .replace(/\s+/g, " ")
                .trim();

        if (!cleanText) {
            return [];
        }

        const sentenceParts =
            cleanText.match(
                /[^.!?।॥\n]+[.!?।॥]?/g
            ) ||
            [cleanText];

        const chunks = [];

        let currentChunk = "";

        function pushWords(
            value
        ) {
            const words =
                value
                    .split(/\s+/)
                    .filter(Boolean);

            let wordChunk = "";

            words.forEach(
                function (word) {
                    const nextWordChunk =
                        wordChunk
                            ? wordChunk + " " + word
                            : word;

                    if (
                        utf8Length(
                            nextWordChunk
                        ) >
                        TTS_MAX_CHUNK_BYTES &&
                        wordChunk
                    ) {
                        chunks.push(
                            wordChunk
                        );

                        wordChunk =
                            word;
                    } else {
                        wordChunk =
                            nextWordChunk;
                    }
                }
            );

            if (wordChunk) {
                currentChunk =
                    wordChunk;
            }
        }

        sentenceParts.forEach(
            function (part) {
                const sentence =
                    part.trim();

                if (!sentence) {
                    return;
                }

                const nextChunk =
                    currentChunk
                        ? currentChunk +
                          " " +
                          sentence
                        : sentence;

                if (
                    utf8Length(
                        nextChunk
                    ) <=
                    TTS_MAX_CHUNK_BYTES
                ) {
                    currentChunk =
                        nextChunk;

                    return;
                }

                if (currentChunk) {
                    chunks.push(
                        currentChunk
                    );

                    currentChunk =
                        "";
                }

                if (
                    utf8Length(
                        sentence
                    ) >
                    TTS_MAX_CHUNK_BYTES
                ) {
                    pushWords(
                        sentence
                    );
                } else {
                    currentChunk =
                        sentence;
                }
            }
        );

        if (currentChunk) {
            chunks.push(
                currentChunk
            );
        }

        return chunks;
    }


    async function fetchTtsAudio(
        text,
        signal
    ) {
        const response =
            await fetch(
                "/api/tts",
                {
                    method: "POST",

                    signal: signal,

                    credentials:
                        "same-origin",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "Accept":
                            "audio/mpeg",
                    },

                    body:
                        JSON.stringify({
                            text: text,

                            languageCode:
                                userLanguageCode,
                        }),
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
                console.log(
                    "TTS error response parse failed:",
                    error
                );
            }

            throw new Error(
                errorMessage
            );
        }

        return response.blob();
    }


    async function playSpeechChunk(
        audioBlob,
        chunkText,
        spokenPrefix,
        liveTextElement,
        runId
    ) {
        if (
            runId !== speechRunId ||
            !voiceReplyEnabled ||
            !pageIsVisible
        ) {
            return "cancelled";
        }

        resetAudioElement();

        activeAudioObjectUrl =
            URL.createObjectURL(
                audioBlob
            );

        audioPlayer.src =
            activeAudioObjectUrl;

        return new Promise(
            function (
                resolve,
                reject
            ) {
                let wordTimer = null;
                let settled = false;

                function clearWordTimer() {
                    if (wordTimer) {
                        window.clearInterval(
                            wordTimer
                        );

                        wordTimer = null;
                    }
                }

                function finish(
                    result
                ) {
                    if (settled) {
                        return;
                    }

                    settled = true;

                    clearWordTimer();

                    audioPlayer.onloadedmetadata =
                        null;

                    audioPlayer.onended =
                        null;

                    audioPlayer.onerror =
                        null;

                    currentSpeechCancel =
                        null;

                    resolve(
                        result
                    );
                }

                currentSpeechCancel =
                    function () {
                        if (
                            liveTextElement &&
                            currentSpeechDisplay
                        ) {
                            liveTextElement.textContent =
                                currentSpeechDisplay.fullText;
                        }

                        finish(
                            "cancelled"
                        );
                    };


                function startWordSync() {
                    if (!liveTextElement) {
                        return;
                    }

                    const words =
                        chunkText
                            .split(/\s+/)
                            .filter(Boolean);

                    let wordIndex = 0;

                    const duration =
                        Number(
                            audioPlayer.duration
                        );

                    const totalDuration =
                        Number.isFinite(
                            duration
                        ) &&
                        duration > 0
                            ? duration * 1000
                            : Math.max(
                                words.length * 360,
                                1200
                            );

                    const interval =
                        Math.max(
                            90,
                            totalDuration /
                            Math.max(
                                words.length,
                                1
                            )
                        );

                    liveTextElement.textContent =
                        spokenPrefix;

                    wordTimer =
                        window.setInterval(
                            function () {
                                if (
                                    wordIndex >=
                                    words.length
                                ) {
                                    clearWordTimer();
                                    return;
                                }

                                const prefix =
                                    liveTextElement.textContent
                                        ? " "
                                        : "";

                                liveTextElement.textContent +=
                                    prefix +
                                    words[
                                        wordIndex
                                    ];

                                wordIndex += 1;

                                scrollMessagesToBottom();
                            },
                            interval
                        );
                }


                audioPlayer.onloadedmetadata =
                    startWordSync;


                audioPlayer.onended =
                    function () {
                        clearWordTimer();

                        if (
                            liveTextElement
                        ) {
                            liveTextElement.textContent =
                                [
                                    spokenPrefix,
                                    chunkText
                                ]
                                    .filter(Boolean)
                                    .join(" ");
                        }

                        resetAudioElement();

                        finish(
                            "ended"
                        );
                    };


                audioPlayer.onerror =
                    function () {
                        const mediaError =
                            audioPlayer.error;

                        resetAudioElement();

                        currentSpeechCancel =
                            null;

                        reject(
                            new Error(
                                mediaError
                                    ? "Laxmi audio playback failed. Media code: " +
                                      mediaError.code
                                    : "Laxmi audio playback failed."
                            )
                        );
                    };


                const playPromise =
                    audioPlayer.play();

                Promise.resolve(
                    playPromise
                )
                    .then(
                        function () {
                            if (
                                runId !==
                                speechRunId
                            ) {
                                finish(
                                    "cancelled"
                                );

                                return;
                            }

                            isSpeaking =
                                true;

                            audioPlaybackUnlocked =
                                true;

                            characterSection.classList.add(
                                "is-speaking"
                            );

                            setAvatarState(
                                "speaking"
                            );

                            setStopSpeakingVisible(
                                true
                            );

                            status.textContent =
                                "Laxmi is speaking...";

                            voiceStatus.textContent =
                                "Laxmi is speaking...";
                        }
                    )
                    .catch(
                        function (error) {
                            clearWordTimer();

                            resetAudioElement();

                            currentSpeechCancel =
                                null;

                            if (
                                error &&
                                error.name ===
                                    "NotAllowedError"
                            ) {
                                audioPlaybackUnlocked =
                                    false;

                                finish(
                                    "blocked"
                                );

                                return;
                            }

                            reject(
                                error
                            );
                        }
                    );
            }
        );
    }


    /* =====================================================
       MAIN SPEAK
    ===================================================== */

    async function speakText(
        text,
        liveTextElement
    ) {
        const fullText =
            String(text || "")
                .trim();

        if (!fullText) {
            return;
        }

        if (
            !voiceReplyEnabled ||
            !pageIsVisible
        ) {
            if (liveTextElement) {
                liveTextElement.textContent =
                    fullText;
            }

            resetAssistantVisuals();

            return;
        }

        stopAssistantSpeech({
            resetVisuals: false,
            keepVoiceStatus: true,
        });

        const runId =
            ++speechRunId;

        const chunks =
            splitSpeechText(
                fullText
            );

        let spokenPrefix = "";

        currentSpeechDisplay = {
            element:
                liveTextElement,

            fullText:
                fullText,
        };

        if (liveTextElement) {
            liveTextElement.textContent =
                "";
        }

        try {
            for (
                const chunk of chunks
            ) {
                if (
                    runId !== speechRunId ||
                    !voiceReplyEnabled ||
                    !pageIsVisible
                ) {
                    break;
                }

                currentTtsController =
                    new AbortController();

                const audioBlob =
                    await fetchTtsAudio(
                        chunk,
                        currentTtsController.signal
                    );

                currentTtsController =
                    null;

                const result =
                    await playSpeechChunk(
                        audioBlob,
                        chunk,
                        spokenPrefix,
                        liveTextElement,
                        runId
                    );

                if (
                    result === "blocked"
                ) {
                    if (
                        liveTextElement
                    ) {
                        liveTextElement.textContent =
                            fullText;
                    }

                    pendingSpeech = {
                        text:
                            fullText,

                        element:
                            liveTextElement,
                    };

                    isSpeaking =
                        false;

                    characterSection.classList.remove(
                        "is-speaking"
                    );

                    setStopSpeakingVisible(
                        false
                    );

                    setAvatarState(
                        "idle"
                    );

                    voiceStatus.textContent =
                        "iPhone Safari blocked autoplay. Tap the speaker button once.";

                    status.textContent =
                        "Tap speaker to play voice";

                    return;
                }

                if (
                    result === "cancelled"
                ) {
                    break;
                }

                spokenPrefix =
                    [
                        spokenPrefix,
                        chunk
                    ]
                        .filter(Boolean)
                        .join(" ");
            }

        } catch (error) {
            if (
                error &&
                error.name ===
                    "AbortError"
            ) {
                return;
            }

            if (
                liveTextElement
            ) {
                liveTextElement.textContent =
                    fullText;
            }

            throw error;

        } finally {
            if (
                runId === speechRunId
            ) {
                if (
                    liveTextElement
                ) {
                    liveTextElement.textContent =
                        fullText;
                }

                currentSpeechDisplay =
                    null;

                currentTtsController =
                    null;

                currentSpeechCancel =
                    null;

                isSpeaking =
                    false;

                characterSection.classList.remove(
                    "is-speaking"
                );

                setStopSpeakingVisible(
                    false
                );

                if (!pendingSpeech) {
                    resetAssistantVisuals();

                    voiceStatus.textContent =
                        voiceReplyEnabled
                            ? "Type or tap microphone"
                            : "Voice reply is off";
                }
            }
        }
    }


    async function replayPendingSpeech() {
        if (
            !pendingSpeech ||
            !voiceReplyEnabled
        ) {
            return false;
        }

        const pending =
            pendingSpeech;

        const unlocked =
            await unlockAudioPlayback();

        if (!unlocked) {
            voiceStatus.textContent =
                "Tap the speaker button again to allow voice playback.";

            return true;
        }

        pendingSpeech = null;

        try {
            await speakText(
                pending.text,
                pending.element
            );

        } catch (error) {
            showError(
                error.message ||
                "Unable to play voice."
            );
        }

        return true;
    }


    /* =====================================================
       VOICE INPUT CLEANUP
    ===================================================== */

    function clearVoiceSilenceTimer() {
        if (voiceSilenceTimer) {
            window.clearTimeout(
                voiceSilenceTimer
            );

            voiceSilenceTimer =
                null;
        }
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

        iosMediaStream =
            null;
    }


    function clearIOSRecordingTimers() {
        if (iosMaximumTimer) {
            window.clearTimeout(
                iosMaximumTimer
            );

            iosMaximumTimer =
                null;
        }
    }


    function updateIOSMicUI(
        recording
    ) {
        iosIsRecording =
            Boolean(recording);

        isListening =
            Boolean(recording);

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


    function stopVoiceInputActivity() {
        iosVoiceRunId += 1;
        iosActiveRunId = 0;

        clearVoiceSilenceTimer();

        recognitionShouldRestart =
            false;

        accumulatedVoiceText =
            "";

        recognitionSessionBaseText =
            "";

        recognitionFinalSegments.clear();

        if (recognition) {
            try {
                recognition.abort();

            } catch (error) {
                console.log(
                    "Recognition abort error:",
                    error
                );
            }

            recognition =
                null;
        }

        if (
            iosTranscriptionController
        ) {
            iosTranscriptionController.abort();

            iosTranscriptionController =
                null;
        }

        clearIOSRecordingTimers();

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

        iosMediaRecorder =
            null;

        iosAudioChunks =
            [];

        iosRecordingStartedAt =
            0;

        iosStopPromise =
            null;

        updateIOSMicUI(
            false
        );

        releaseIOSMediaStream();

        isListening =
            false;

        micButton.disabled =
            false;

        micButton.classList.remove(
            "is-listening"
        );

        micButton.innerHTML =
            '<i class="bi bi-mic-fill"></i>';
    }


    /* =====================================================
       STOP ALL ACTIVITY
    ===================================================== */

    function stopCurrentAssistantActivity(
        options
    ) {
        const settings =
            options || {};

        stopAssistantSpeech({
            resetVisuals: false,
            keepVoiceStatus: true,
        });

        stopVoiceInputActivity();

        if (
            settings.abortChat !== false &&
            currentChatController
        ) {
            currentChatController.abort();

            currentChatController =
                null;
        }

        isSending =
            false;

        thinking.hidden =
            true;

        status.textContent =
            "Online";

        voiceStatus.textContent =
            voiceReplyEnabled
                ? "Type or tap microphone"
                : "Voice reply is off";

        resetAssistantVisuals();

        updateCharacterCount();
    }


    /* =====================================================
       GREETING
    ===================================================== */

    async function typeGreeting(
        text
    ) {
        const currentRunId =
            ++greetingRunId;

        introBubble.textContent =
            "";

        for (
            const letter of String(
                text || ""
            )
        ) {
            if (
                currentRunId !==
                greetingRunId
            ) {
                return;
            }

            introBubble.textContent +=
                letter;

            await wait(
                18
            );
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
                        method:
                            "GET",

                        credentials:
                            "same-origin",

                        headers: {
                            "Accept":
                                "application/json",
                        },
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

            await wait(
                1050
            );

            const greetingText =
                String(
                    data.greeting ||
                    "Welcome. I am Laxmi, your Basha AI Assistant. How can I help you?"
                ).trim();

            introBubble.textContent =
                "";

            status.textContent =
                "Laxmi is speaking...";

            voiceStatus.textContent =
                "Please listen...";

            await speakText(
                greetingText,
                introBubble
            );

            if (!pendingSpeech) {
                status.textContent =
                    "Ready";

                voiceStatus.textContent =
                    "Tap microphone or type your question";
            }

        } catch (error) {
            console.log(
                "Greeting error:",
                error
            );

            const fallbackGreeting =
                "Hi. I am Laxmi, your Basha AI Assistant. How can I help you?";

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
       OPEN ANIMATION
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

            width:
                size,

            height:
                size,
        };
    }


    function setFlyingAvatarRect(
        rectangle
    ) {
        flyingAvatar.style.left =
            rectangle.left +
            "px";

        flyingAvatar.style.top =
            rectangle.top +
            "px";

        flyingAvatar.style.width =
            rectangle.width +
            "px";

        flyingAvatar.style.height =
            rectangle.height +
            "px";
    }


    function resetFlyingAvatarStyles() {
        flyingAvatar.style.transform =
            "";

        flyingAvatar.style.opacity =
            "";
    }


    async function animateOpen() {
        if (
            isAnimating ||
            !shell.hidden
        ) {
            return;
        }

        isAnimating =
            true;

        hideError();

        primeSpeechSynthesis();

        void unlockAudioPlayback();

        stopVoiceInputActivity();

        resetFlyingAvatarStyles();

        updateAiMobileViewport();

        const flyingImage =
            flyingAvatar.querySelector(
                "img"
            );

        if (flyingImage) {
            flyingImage.src =
                avatarFrames.idle[0] ||
                avatarFrames.fallback;
        }

        shell.hidden =
            false;

        shell.classList.remove(
            "is-open",
            "character-ready"
        );

        introBubble.classList.remove(
            "show"
        );

        resetAssistantVisuals();

        const startRect =
            topAvatar
                .getBoundingClientRect();

        setFlyingAvatarRect(
            startRect
        );

        flyingAvatar.hidden =
            false;

        openButton.classList.add(
            "is-hidden"
        );

        lockPageScroll();

        await wait(
            30
        );

        shell.classList.add(
            "is-open"
        );

        await wait(
            110
        );

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
                                    "translate3d(0,0,0) scale(1)",

                                opacity:
                                    1,
                            },

                            {
                                transform:
                                    "translate3d(" +
                                    (deltaX * 0.52) +
                                    "px," +
                                    (deltaY * 0.24) +
                                    "px,0) " +
                                    "scale(1.30) rotate(-7deg)",

                                opacity:
                                    1,

                                offset:
                                    0.45,
                            },

                            {
                                transform:
                                    "translate3d(" +
                                    deltaX +
                                    "px," +
                                    deltaY +
                                    "px,0) " +
                                    "scale(" +
                                    scaleX +
                                    "," +
                                    scaleY +
                                    ") rotate(0deg)",

                                opacity:
                                    1,
                            },
                        ],
                        {
                            duration:
                                760,

                            easing:
                                "cubic-bezier(.18,.84,.32,1)",

                            fill:
                                "forwards",
                        }
                    );

                await animation.finished;

            } else {
                await wait(
                    400
                );
            }

        } catch (error) {
            console.log(
                "AI open animation error:",
                error
            );
        }

        flyingAvatar.hidden =
            true;

        resetFlyingAvatarStyles();

        shell.classList.add(
            "character-ready"
        );

        introBubble.classList.add(
            "show"
        );

        isAnimating =
            false;

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
            hasWelcomed =
                true;

            await loadGreeting();

        } else {
            introBubble.classList.remove(
                "show"
            );

            status.textContent =
                "Online";

            voiceStatus.textContent =
                voiceReplyEnabled
                    ? "Type or tap microphone"
                    : "Voice reply is off";

            isSending =
                false;

            micButton.disabled =
                false;

            setupSpeechRecognition();

            updateCharacterCount();
        }
    }


    /* =====================================================
       CLOSE ANIMATION
    ===================================================== */

    async function animateClose() {
        if (
            isAnimating ||
            shell.hidden
        ) {
            return;
        }

        isAnimating =
            true;

        greetingRunId += 1;

        stopCurrentAssistantActivity({
            abortChat:
                true
        });

        stopAvatarAnimation();

        if (blinkTimer) {
            window.clearTimeout(
                blinkTimer
            );

            blinkTimer =
                null;
        }

        const characterRect =
            character
                .getBoundingClientRect();

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

            width:
                startSize,

            height:
                startSize,
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

        flyingAvatar.hidden =
            false;

        shell.classList.remove(
            "character-ready"
        );

        introBubble.classList.remove(
            "show"
        );

        await wait(
            30
        );

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

                                opacity:
                                    1,
                            },

                            {
                                transform:
                                    "translate3d(" +
                                    (deltaX * 0.55) +
                                    "px," +
                                    (deltaY * 0.72) +
                                    "px,0) " +
                                    "scale(.82) rotate(7deg)",

                                opacity:
                                    1,

                                offset:
                                    0.55,
                            },

                            {
                                transform:
                                    "translate3d(" +
                                    deltaX +
                                    "px," +
                                    deltaY +
                                    "px,0) " +
                                    "scale(" +
                                    scaleX +
                                    "," +
                                    scaleY +
                                    ") rotate(0deg)",

                                opacity:
                                    0.96,
                            },
                        ],
                        {
                            duration:
                                620,

                            easing:
                                "cubic-bezier(.4,0,.2,1)",

                            fill:
                                "forwards",
                        }
                    );

                await animation.finished;

            } else {
                await wait(
                    300
                );
            }

        } catch (error) {
            console.log(
                "AI close animation error:",
                error
            );
        }

        flyingAvatar.hidden =
            true;

        resetFlyingAvatarStyles();

        shell.hidden =
            true;

        shell.classList.remove(
            "keyboard-open"
        );

        openButton.classList.remove(
            "is-hidden"
        );

        unlockPageScroll();

        resetAssistantVisuals();

        isAnimating =
            false;
    }


    /* =====================================================
       CLEAR CONVERSATION
    ===================================================== */

    function clearConversation() {
        stopCurrentAssistantActivity({
            abortChat:
                true
        });

        conversationHistory =
            [];

        messages.innerHTML =
            "";

        input.value =
            "";

        introBubble.textContent =
            "";

        introBubble.classList.remove(
            "show"
        );

        resizeInput();

        hideError();

        thinking.hidden =
            true;

        status.textContent =
            "Online";

        voiceStatus.textContent =
            voiceReplyEnabled
                ? "Type or tap microphone"
                : "Voice reply is off";

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

        stopAssistantSpeech({
            resetVisuals:
                false,

            keepVoiceStatus:
                true,
        });

        await addMessage(
            "user",
            message,
            false
        );

        input.value =
            "";

        resizeInput();

        isSending =
            true;

        updateCharacterCount();

        thinking.hidden =
            false;

        micButton.disabled =
            true;

        status.textContent =
            "Laxmi is thinking...";

        voiceStatus.textContent =
            "Preparing answer...";

        setAvatarState(
            "thinking"
        );

        scrollMessagesToBottom();

        try {
            await wait(
                AI_REPLY_DELAY
            );

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

            if (
                currentChatController
            ) {
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
                                "application/json",
                        },

                        body:
                            JSON.stringify({
                                message:
                                    message,

                                history:
                                    historyForRequest,
                            }),
                    }
                );

            const data =
                await response.json();

            currentChatController =
                null;

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

            thinking.hidden =
                true;

            const assistantContent =
                createMessage(
                    "assistant",
                    data.reply
                );

            if (
                voiceReplyEnabled &&
                pageIsVisible
            ) {
                status.textContent =
                    "Laxmi is speaking...";

                voiceStatus.textContent =
                    "Please listen...";

                try {
                    await speakText(
                        data.reply,
                        assistantContent
                    );

                } catch (voiceError) {
                    console.log(
                        "AI voice playback error:",
                        voiceError
                    );

                    assistantContent.textContent =
                        data.reply;

                    showError(
                        voiceError.message ||
                        "The answer is ready, but voice playback failed."
                    );

                    resetAssistantVisuals();
                }

            } else {
                assistantContent.textContent =
                    data.reply;

                resetAssistantVisuals();
            }

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
            isSending =
                false;

            thinking.hidden =
                true;

            micButton.disabled =
                false;

            currentChatController =
                null;

            currentTtsController =
                null;

            clearVoiceSilenceTimer();

            accumulatedVoiceText =
                "";

            recognitionSessionBaseText =
                "";

            recognitionFinalSegments.clear();

            if (
                !isSpeaking &&
                !pendingSpeech
            ) {
                voiceStatus.textContent =
                    voiceReplyEnabled
                        ? "Type or tap microphone"
                        : "Voice reply is off";

                resetAssistantVisuals();
            }

            updateCharacterCount();
        }
    }


    /* =====================================================
       REPEATED SPEECH CLEANUP
    ===================================================== */

    function canonicalSpeechToken(
        token
    ) {
        return String(token || "")
            .toLocaleLowerCase()
            .replace(
                /[^\p{L}\p{N}]+/gu,
                ""
            );
    }


    function normalizeSpeechText(
        text
    ) {
        const tokens =
            String(text || "")
                .replace(/\s+/g, " ")
                .trim()
                .split(" ")
                .filter(Boolean);

        const cleaned =
            [];

        tokens.forEach(
            function (token) {
                const previous =
                    cleaned.length
                        ? canonicalSpeechToken(
                            cleaned[
                                cleaned.length - 1
                            ]
                        )
                        : "";

                const current =
                    canonicalSpeechToken(
                        token
                    );

                if (
                    current &&
                    current === previous
                ) {
                    return;
                }

                cleaned.push(
                    token
                );
            }
        );

        return cleaned
            .join(" ")
            .trim();
    }


    function mergeTranscript(
        baseText,
        additionText
    ) {
        const base =
            normalizeSpeechText(
                baseText
            );

        const addition =
            normalizeSpeechText(
                additionText
            );

        if (!base) {
            return addition;
        }

        if (!addition) {
            return base;
        }

        const baseWords =
            base.split(/\s+/);

        const additionWords =
            addition.split(/\s+/);

        const maximumOverlap =
            Math.min(
                baseWords.length,
                additionWords.length,
                20
            );

        let overlap = 0;

        for (
            let size = maximumOverlap;
            size >= 1;
            size -= 1
        ) {
            const baseTail =
                baseWords
                    .slice(-size)
                    .map(
                        canonicalSpeechToken
                    )
                    .join("|");

            const additionHead =
                additionWords
                    .slice(0, size)
                    .map(
                        canonicalSpeechToken
                    )
                    .join("|");

            if (
                baseTail &&
                baseTail === additionHead
            ) {
                overlap =
                    size;

                break;
            }
        }

        return normalizeSpeechText(
            baseWords
                .concat(
                    additionWords.slice(
                        overlap
                    )
                )
                .join(" ")
        );
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

                    accumulatedVoiceText =
                        "";

                    recognitionShouldRestart =
                        false;

                    voiceSilenceTimer =
                        null;

                    if (!finalVoiceText) {
                        return;
                    }

                    input.value =
                        finalVoiceText;

                    resizeInput();

                    updateCharacterCount();

                    stopListening(
                        true
                    );

                    voiceStatus.textContent =
                        "Sending voice message...";

                    void sendMessage();
                },
                VOICE_SILENCE_DELAY
            );
    }


    /* =====================================================
       IOS AUDIO RECORDING HELPERS
    ===================================================== */

    function getSupportedAudioMimeType() {
        const types = [
            "audio/mp4",
            "audio/webm;codecs=opus",
            "audio/webm",
            "audio/ogg;codecs=opus",
        ];

        for (
            const type of types
        ) {
            if (
                window.MediaRecorder &&
                typeof MediaRecorder.isTypeSupported ===
                    "function" &&
                MediaRecorder.isTypeSupported(
                    type
                )
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

        if (
            type.includes("mp4")
        ) {
            return "m4a";
        }

        if (
            type.includes("ogg")
        ) {
            return "ogg";
        }

        if (
            type.includes("wav")
        ) {
            return "wav";
        }

        if (
            type.includes("mpeg") ||
            type.includes("mp3")
        ) {
            return "mp3";
        }

        return "webm";
    }


    /* =====================================================
       IOS TRANSCRIPTION
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

        if (
            iosTranscriptionController
        ) {
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
            "laxmi-voice." +
            extension
        );

        formData.append(
            "languageCode",
            userLanguageCode ||
            "en"
        );

        const response =
            await fetch(
                "/api/ai-assistant/transcribe",
                {
                    method:
                        "POST",

                    signal:
                        iosTranscriptionController.signal,

                    credentials:
                        "same-origin",

                    body:
                        formData,
                }
            );

        iosTranscriptionController =
            null;

        let data = {};

        try {
            data =
                await response.json();

        } catch (error) {
            console.log(
                "Transcription response parse failed:",
                error
            );
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
            normalizeSpeechText(
                data.transcript ||
                data.text ||
                ""
            );

        if (!transcript) {
            throw new Error(
                "No speech was detected."
            );
        }

        return transcript;
    }


    /* =====================================================
       FINISH IOS RECORDING
    ===================================================== */

    async function finishIOSRecording(
        shouldSend
    ) {
        if (iosStopPromise) {
            return iosStopPromise;
        }

        if (!iosMediaRecorder) {
            updateIOSMicUI(
                false
            );

            releaseIOSMediaStream();

            return;
        }

        const runId =
            iosActiveRunId;

        iosStopPromise =
            (
                async function () {
                    clearIOSRecordingTimers();

                    const recorder =
                        iosMediaRecorder;

                    iosMediaRecorder =
                        null;

                    const recordingDuration =
                        Date.now() -
                        iosRecordingStartedAt;

                    iosRecordingStartedAt =
                        0;

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
                                                            "audio/mp4",
                                                    }
                                                );

                                            iosAudioChunks =
                                                [];

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
                                                        "audio/mp4",
                                                }
                                            );

                                        iosAudioChunks =
                                            [];

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

                    if (
                        !runId ||
                        runId !== iosVoiceRunId ||
                        shell.hidden
                    ) {
                        return;
                    }

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

                    const transcript =
                        await transcribeIOSAudio(
                            audioBlob
                        );

                    if (
                        runId !== iosVoiceRunId ||
                        shell.hidden
                    ) {
                        return;
                    }

                    input.value =
                        transcript;

                    resizeInput();

                    updateCharacterCount();

                    status.textContent =
                        "Voice received";

                    voiceStatus.textContent =
                        "Sending voice message...";

                    await wait(
                        150
                    );

                    await sendMessage();
                }
            )();

        try {
            await iosStopPromise;

        } catch (error) {
            if (
                !(
                    error &&
                    error.name ===
                        "AbortError"
                )
            ) {
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

        } finally {
            iosStopPromise =
                null;

            if (
                runId === iosVoiceRunId
            ) {
                iosActiveRunId =
                    0;
            }
        }
    }


    /* =====================================================
       START IOS RECORDING
    ===================================================== */

    async function startIOSRecording() {
        if (
            isSending ||
            iosIsRecording
        ) {
            return;
        }

        if (
            !supportsMediaRecorder()
        ) {
            showError(
                "Voice recording is not supported in this iPhone browser. Please update iOS or use Safari."
            );

            return;
        }

        hideError();

        iosActiveRunId =
            ++iosVoiceRunId;

        stopAssistantSpeech({
            resetVisuals:
                false,

            keepVoiceStatus:
                true,
        });

        iosAudioChunks =
            [];

        try {
            iosMediaStream =
                await navigator
                    .mediaDevices
                    .getUserMedia({
                        audio: {
                            echoCancellation:
                                true,

                            noiseSuppression:
                                true,

                            autoGainControl:
                                true,
                        },
                    });

            const mimeType =
                getSupportedAudioMimeType();

            iosMediaRecorder =
                mimeType
                    ? new MediaRecorder(
                        iosMediaStream,
                        {
                            mimeType:
                                mimeType
                        }
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

            iosMaximumTimer =
                window.setTimeout(
                    function () {
                        if (
                            iosIsRecording
                        ) {
                            void finishIOSRecording(
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
       ANDROID / CHROME SPEECH RECOGNITION
    ===================================================== */

    function setupSpeechRecognition() {
        if (isIOSDevice()) {
            recognition =
                null;

            const supported =
                supportsMediaRecorder();

            micButton.disabled =
                !supported;

            micButton.classList.remove(
                "is-listening"
            );

            micButton.innerHTML =
                '<i class="bi bi-mic-fill"></i>';

            voiceStatus.textContent =
                supported
                    ? "Tap microphone to record"
                    : "Voice recording is not supported";

            return;
        }


        const SpeechRecognition =
            window.SpeechRecognition ||
            window.webkitSpeechRecognition;


        if (!SpeechRecognition) {
            recognition =
                null;

            micButton.disabled =
                true;

            micButton.classList.remove(
                "is-listening"
            );

            micButton.innerHTML =
                '<i class="bi bi-mic-fill"></i>';

            voiceStatus.textContent =
                "Voice input is not supported in this browser";

            return;
        }


        micButton.disabled =
            false;


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


        recognition.continuous =
            true;

        recognition.interimResults =
            true;

        recognition.maxAlternatives =
            1;

        recognition.lang =
            speechLanguageMap[
                userLanguageCode
            ] ||
            userLanguageCode ||
            "en-IN";


        recognition.onstart =
            function () {
                isListening =
                    true;

                recognitionShouldRestart =
                    true;

                recognitionSessionBaseText =
                    accumulatedVoiceText;

                recognitionFinalSegments =
                    new Map();

                micButton.disabled =
                    false;

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
                const interimSegments =
                    [];

                for (
                    let index = 0;
                    index <
                        event.results.length;
                    index += 1
                ) {
                    const transcript =
                        normalizeSpeechText(
                            event.results[
                                index
                            ][0].transcript ||
                            ""
                        );

                    if (!transcript) {
                        continue;
                    }

                    if (
                        event.results[
                            index
                        ].isFinal
                    ) {
                        recognitionFinalSegments.set(
                            index,
                            transcript
                        );

                    } else {
                        interimSegments.push(
                            transcript
                        );
                    }
                }


                const sessionFinalText =
                    Array.from(
                        recognitionFinalSegments.entries()
                    )
                        .sort(
                            function (
                                first,
                                second
                            ) {
                                return (
                                    first[0] -
                                    second[0]
                                );
                            }
                        )
                        .map(
                            function (entry) {
                                return entry[1];
                            }
                        )
                        .join(" ");


                accumulatedVoiceText =
                    mergeTranscript(
                        recognitionSessionBaseText,
                        sessionFinalText
                    );


                const interimText =
                    normalizeSpeechText(
                        interimSegments.join(
                            " "
                        )
                    );


                const visibleText =
                    mergeTranscript(
                        accumulatedVoiceText,
                        interimText
                    );


                input.value =
                    visibleText;

                resizeInput();

                updateCharacterCount();


                if (interimText) {
                    clearVoiceSilenceTimer();

                    voiceStatus.textContent =
                        "Listening...";

                    status.textContent =
                        "Laxmi is listening...";

                } else if (
                    accumulatedVoiceText
                ) {
                    scheduleVoiceMessageSend();

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
                        350
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


    /* =====================================================
       START LISTENING
    ===================================================== */

    function startListening() {
        if (isSending) {
            return;
        }

        if (isIOSDevice()) {
            void toggleIOSRecording();
            return;
        }

        stopAssistantSpeech({
            resetVisuals:
                false,

            keepVoiceStatus:
                true,
        });

        clearVoiceSilenceTimer();

        accumulatedVoiceText =
            "";

        recognitionSessionBaseText =
            "";

        recognitionFinalSegments.clear();

        recognitionShouldRestart =
            true;

        if (!recognition) {
            setupSpeechRecognition();
        }

        if (!recognition) {
            return;
        }

        hideError();

        input.value =
            "";

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


    /* =====================================================
       STOP LISTENING
    ===================================================== */

    function stopListening(
        keepSilenceTimer
    ) {
        recognitionShouldRestart =
            false;

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

        isListening =
            false;

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
       IOS USER GESTURE AUDIO ACTIVATION
    ===================================================== */

    function installAudioActivationHandlers(
        element
    ) {
        if (!element) {
            return;
        }

        element.addEventListener(
            "pointerdown",
            function () {
                primeSpeechSynthesis();

                void unlockAudioPlayback();
            },
            {
                passive:
                    true
            }
        );
    }


    installAudioActivationHandlers(
        openButton
    );

    installAudioActivationHandlers(
        panel
    );

    installAudioActivationHandlers(
        sendButton
    );

    installAudioActivationHandlers(
        micButton
    );

    installAudioActivationHandlers(
        voiceToggle
    );


    /* =====================================================
       MAIN EVENTS
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


    /* =====================================================
       STOP SPEAKING BUTTON
    ===================================================== */

    stopSpeakingButton.addEventListener(
        "click",
        function () {
            stopAssistantSpeech();

            status.textContent =
                "Online";

            voiceStatus.textContent =
                voiceReplyEnabled
                    ? "Speaking stopped"
                    : "Voice reply is off";
        }
    );


    /* =====================================================
       VOICE ON / OFF
    ===================================================== */

    voiceToggle.addEventListener(
        "click",
        async function () {
            hideError();

            if (
                await replayPendingSpeech()
            ) {
                return;
            }

            voiceReplyEnabled =
                !voiceReplyEnabled;

            localStorage.setItem(
                "bashaAiVoiceReply",
                voiceReplyEnabled
                    ? "on"
                    : "off"
            );

            if (!voiceReplyEnabled) {
                stopAssistantSpeech({
                    resetVisuals:
                        true,

                    keepVoiceStatus:
                        true,
                });

                status.textContent =
                    "Voice Off";

                voiceStatus.textContent =
                    "Voice reply is off";

            } else {
                primeSpeechSynthesis();

                await unlockAudioPlayback();

                status.textContent =
                    "Online";

                voiceStatus.textContent =
                    "Voice reply is on";
            }

            updateVoiceToggleUI();
        }
    );


    /* =====================================================
       MICROPHONE BUTTON
    ===================================================== */

    micButton.addEventListener(
        "click",
        async function () {
            hideError();

            await unlockAudioPlayback();


            if (isIOSDevice()) {
                await toggleIOSRecording();

                return;
            }


            if (isListening) {
                recognitionShouldRestart =
                    false;

                clearVoiceSilenceTimer();

                stopListening();

                await wait(
                    180
                );


                const spokenText =
                    normalizeSpeechText(
                        accumulatedVoiceText ||
                        input.value ||
                        ""
                    );


                if (spokenText) {
                    accumulatedVoiceText =
                        "";

                    recognitionSessionBaseText =
                        "";

                    recognitionFinalSegments.clear();

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
                stopAssistantSpeech();
            }


            startListening();
        }
    );


    /* =====================================================
       SEND
    ===================================================== */

    sendButton.addEventListener(
        "click",
        sendMessage
    );


    /* =====================================================
       TEXTAREA
    ===================================================== */

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

                void sendMessage();
            }
        }
    );


    input.addEventListener(
        "focus",
        function () {
            window.setTimeout(
                updateAiMobileViewport,
                80
            );
        }
    );


    input.addEventListener(
        "blur",
        function () {
            window.setTimeout(
                updateAiMobileViewport,
                120
            );
        }
    );


    /* =====================================================
       ESC CLOSE
    ===================================================== */

    document.addEventListener(
        "keydown",
        function (event) {
            if (
                event.key === "Escape" &&
                !shell.hidden
            ) {
                void animateClose();
            }
        }
    );


    /* =====================================================
       PAGE VISIBILITY
       BACKGROUND LO VOICE CONTINUE KAKUDADHU
    ===================================================== */

    document.addEventListener(
        "visibilitychange",
        function () {
            pageIsVisible =
                document.visibilityState ===
                "visible";


            if (!pageIsVisible) {
                stopAssistantSpeech({
                    resetVisuals:
                        false,

                    keepVoiceStatus:
                        true,
                });

                stopVoiceInputActivity();


                if (blinkTimer) {
                    window.clearTimeout(
                        blinkTimer
                    );

                    blinkTimer =
                        null;
                }

                return;
            }


            if (!shell.hidden) {
                updateAiMobileViewport();

                setAvatarState(
                    "idle"
                );

                scheduleBlink();
            }
        }
    );


    /* =====================================================
       PAGE HIDE / UNLOAD
    ===================================================== */

    window.addEventListener(
        "pagehide",
        function () {
            stopCurrentAssistantActivity({
                abortChat:
                    true
            });
        }
    );


    window.addEventListener(
        "beforeunload",
        function () {
            stopCurrentAssistantActivity({
                abortChat:
                    true
            });

            stopAvatarAnimation();
        }
    );


    /* =====================================================
       MOBILE VIEWPORT EVENTS
    ===================================================== */

    window.addEventListener(
        "resize",
        updateAiMobileViewport
    );


    window.addEventListener(
        "orientationchange",
        updateAiMobileViewport
    );


    if (
        window.visualViewport
    ) {
        window.visualViewport.addEventListener(
            "resize",
            updateAiMobileViewport
        );

        window.visualViewport.addEventListener(
            "scroll",
            updateAiMobileViewport
        );
    }


    /* =====================================================
       SPEECH VOICES
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


    setStopSpeakingVisible(
        false
    );


    updateVoiceToggleUI();


    setupSpeechRecognition();


    updateCharacterCount();


    updateAiMobileViewport();
});