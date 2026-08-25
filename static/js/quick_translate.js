document.addEventListener(
    "DOMContentLoaded",
    () => {

    const card =
        document.getElementById(
            "quickTranslateCard"
        );

    if (!card) {
        return;
    }


    /* =========================================
       MAIN ELEMENTS
    ========================================= */

    const toggle =
        document.getElementById(
            "qtToggle"
        );

    const collapse =
        document.getElementById(
            "qtCollapse"
        );

    const source =
        document.getElementById(
            "qtSourceLanguage"
        );

    const target =
        document.getElementById(
            "qtTargetLanguage"
        );

    const swap =
        document.getElementById(
            "qtSwapBtn"
        );

    const input =
        document.getElementById(
            "qtInput"
        );

    const charCount =
        document.getElementById(
            "qtCharCount"
        );

    const sourceLabel =
        document.getElementById(
            "qtSourceLabel"
        );

    const resultLanguage =
        document.getElementById(
            "qtResultLanguage"
        );

    const resultCount =
        document.getElementById(
            "qtResultCount"
        );

    const clearBtn =
        document.getElementById(
            "qtClearBtn"
        );

    const errorBox =
        document.getElementById(
            "qtError"
        );

    const outputPlaceholder =
        document.getElementById(
            "qtOutputPlaceholder"
        );

    const loading =
        document.getElementById(
            "qtLoading"
        );

    const translatedText =
        document.getElementById(
            "qtTranslatedText"
        );

    const autoStatus =
        document.getElementById(
            "qtAutoStatus"
        );

    const copyBtn =
        document.getElementById(
            "qtCopyBtn"
        );

    const copyActionBtn =
        document.getElementById(
            "qtCopyActionBtn"
        );

    const sendBtn =
        document.getElementById(
            "qtSendBtn"
        );


    /* FILE BUTTONS */

    const cameraBtn =
        document.getElementById(
            "qtCameraBtn"
        );

    const imageBtn =
        document.getElementById(
            "qtImageBtn"
        );

    const documentBtn =
        document.getElementById(
            "qtDocumentBtn"
        );

    const cameraInput =
        document.getElementById(
            "qtCameraInput"
        );

    const imageInput =
        document.getElementById(
            "qtImageInput"
        );

    const documentInput =
        document.getElementById(
            "qtDocumentInput"
        );

    const selectedFile =
        document.getElementById(
            "qtSelectedFile"
        );

    const selectedFileName =
        document.getElementById(
            "qtSelectedFileName"
        );

    const selectedFileStatus =
        document.getElementById(
            "qtSelectedFileStatus"
        );

    const selectedFileRemove =
        document.getElementById(
            "qtSelectedFileRemove"
        );

    /* LIVE CAMERA */

    const liveCameraBtn =
    document.getElementById(
        "qtLiveCameraBtn"
    );

    const liveCameraBox =
        document.getElementById(
            "qtLiveCamera"
        );

    const liveCameraVideo =
        document.getElementById(
            "qtLiveCameraVideo"
        );

    const liveCameraCanvas =
        document.getElementById(
            "qtLiveCameraCanvas"
        );

    const liveCameraClose =
        document.getElementById(
            "qtLiveCameraClose"
        );

    const liveCameraSwitch =
        document.getElementById(
            "qtLiveCameraSwitch"
        );

    const liveCameraStatus =
        document.getElementById(
            "qtLiveCameraStatus"
        );

    const liveCameraBadgeText =
        document.getElementById(
            "qtLiveCameraBadgeText"
        );

    const liveCameraOverlay =
        document.getElementById(
            "qtLiveCameraOverlay"
        );

    const liveDetectedLanguage =
        document.getElementById(
            "qtLiveDetectedLanguage"
        );

    const liveTranslatedText =
        document.getElementById(
            "qtLiveTranslatedText"
        );    


    /* AUDIO */

    const audioBtn =
        document.getElementById(
            "qtAudioBtn"
        );

    const recorderBox =
        document.getElementById(
            "qtRecorder"
        );

    const recorderTitle =
        document.getElementById(
            "qtRecorderTitle"
        );

    const recorderStatus =
        document.getElementById(
            "qtRecorderStatus"
        );

    const recordTime =
        document.getElementById(
            "qtRecordTime"
        );

    const recordStart =
        document.getElementById(
            "qtRecordStart"
        );

    const recordStop =
        document.getElementById(
            "qtRecordStop"
        );

    const recordCancel =
        document.getElementById(
            "qtRecordCancel"
        );

    const audioResult =
        document.getElementById(
            "qtAudioResult"
        );

    const translatedAudio =
        document.getElementById(
            "qtTranslatedAudio"
        );

    const detectedLanguage =
        document.getElementById(
            "qtDetectedLanguage"
        );


    /* STATE */

    let latestTranslation = "";

    let translationTimer = null;

    let activeController = null;

    let translationRequestNumber = 0;


    let mediaRecorder = null;

    let microphoneStream = null;

    let audioChunks = [];

    let recordingTimer = null;

    let recordingSeconds = 0;

    let latestAudioBlob = null;

    let latestAudioFilename =
        "basha-recording.webm";

    let audioTranslateController = null;

    let audioTranslateRequestNumber = 0;

    let audioSessionNumber = 0;

    let audioTranslationRunning = false;
    
    let liveCameraStream = null;

    let liveCameraTimer = null;

    let liveCameraRequestController = null;

    let liveCameraRunning = false;

    let liveCameraFacingMode =
        "environment";

    let liveCameraScanning = false;

    let lastLiveFrameSignature = "";

    let lastLiveTranslatedText = "";

    let liveCameraGeneration = 0;


    /* =========================================
       HELPERS
    ========================================= */

    function escapeHtml(value) {

        return String(
            value ?? ""
        )
            .replaceAll(
                "&",
                "&amp;"
            )
            .replaceAll(
                "<",
                "&lt;"
            )
            .replaceAll(
                ">",
                "&gt;"
            )
            .replaceAll(
                '"',
                "&quot;"
            )
            .replaceAll(
                "'",
                "&#039;"
            );
    }


    function getLanguageName(
        selectElement
    ) {

        const option =
            selectElement.options[
                selectElement.selectedIndex
            ];

        return option
            ? option.textContent.trim()
            : "";
    }


    function openCard() {

        collapse.hidden = false;

        toggle.setAttribute(
            "aria-expanded",
            "true"
        );
    }


    function closeCard() {

        collapse.hidden = true;

        toggle.setAttribute(
            "aria-expanded",
            "false"
        );
    }


    function setActionsEnabled(
        enabled
    ) {

        copyBtn.disabled =
            !enabled;

        copyActionBtn.disabled =
            !enabled;

        sendBtn.disabled =
            !enabled;
    }


    function hideError() {

        errorBox.hidden = true;

        errorBox.textContent = "";
    }


    function showError(message) {

        errorBox.textContent =
            message ||
            "Unable to translate.";

        errorBox.hidden = false;
    }


    function hideAudioResult() {

        if (translatedAudio) {

            try {
                translatedAudio.pause();
            } catch (_) {}

            translatedAudio.removeAttribute(
                "src"
            );

            translatedAudio.load();
        }

        if (audioResult) {
            audioResult.hidden =
                true;
        }

        if (detectedLanguage) {
            detectedLanguage.textContent =
                "";
        }
    }


    function showEmptyOutput() {

        latestTranslation = "";

        loading.hidden =
            true;

        translatedText.hidden =
            true;

        translatedText.textContent =
            "";

        outputPlaceholder.hidden =
            false;

        resultCount.textContent =
            "0 characters";

        resultLanguage.textContent =
            "Choose a target language";

        autoStatus.textContent =
            "Ready";

        hideAudioResult();

        setActionsEnabled(
            false
        );
    }


    function showLoadingOutput(
        statusText = "Translating"
    ) {

        outputPlaceholder.hidden =
            true;

        translatedText.hidden =
            true;

        loading.hidden =
            false;

        autoStatus.innerHTML = `
            <span class="spinner-border spinner-border-sm"></span>
            ${escapeHtml(statusText)}
        `;

        setActionsEnabled(
            false
        );
    }


    function showTranslatedOutput(
        data
    ) {

        latestTranslation =
            String(
                data.translated || ""
            ).trim();

        loading.hidden =
            true;

        outputPlaceholder.hidden =
            true;

        translatedText.textContent =
            latestTranslation;

        translatedText.hidden =
            false;

        resultLanguage.textContent =
            `${
                data.sourceLanguageName ||
                "Auto Detected"
            } → ${
                data.targetLanguageName ||
                getLanguageName(target)
            }`;

        sourceLabel.textContent =
            data.sourceLanguageName ||
            getLanguageName(source);

        resultCount.textContent =
            `${latestTranslation.length} character${
                latestTranslation.length === 1
                    ? ""
                    : "s"
            }`;

        autoStatus.innerHTML = `
            <i class="bi bi-check-circle-fill"></i>
            Translated
        `;

        setActionsEnabled(
            Boolean(
                latestTranslation
            )
        );
    }


    function cancelPendingTranslation() {

        clearTimeout(
            translationTimer
        );

        translationTimer = null;

        if (activeController) {

            activeController.abort();

            activeController = null;
        }
    }


    /* =========================================
       FILE TRANSLATION
    ========================================= */

    function resetFileInputs() {

        if (cameraInput) {
            cameraInput.value = "";
        }

        if (imageInput) {
            imageInput.value = "";
        }

        if (documentInput) {
            documentInput.value = "";
        }

        if (selectedFile) {
            selectedFile.hidden = true;
        }

        if (selectedFileName) {

            selectedFileName.textContent =
                "Selected file";
        }

        if (selectedFileStatus) {

            selectedFileStatus.textContent =
                "";
        }
    }


    function showSelectedFile(
        file,
        statusText
    ) {

        if (!selectedFile) {
            return;
        }

        selectedFile.hidden =
            false;

        selectedFileName.textContent =
            file.name ||
            "Selected file";

        selectedFileStatus.textContent =
            statusText ||
            "Reading and translating...";
    }


    function setInputToolsDisabled(
        disabled
    ) {

        [
            cameraBtn,
            liveCameraBtn,
            imageBtn,
            documentBtn,
            audioBtn
        ].forEach(
            (button) => {

                if (button) {

                    button.disabled =
                        disabled;
                }
            }
        );
    }


    async function translateSelectedFile(
        file
    ) {

        if (!file) {
            return;
        }

        stopRecordingImmediately(
            false
        );

        closeRecorder();

        hideAudioResult();

        latestAudioBlob =
            null;

        const maximumSize =
            15 * 1024 * 1024;

        if (
            file.size >
            maximumSize
        ) {

            showError(
                "File size must be below 15 MB."
            );

            resetFileInputs();

            return;
        }

        cancelPendingTranslation();

        hideError();

        showSelectedFile(
            file,
            "Detecting language and translating..."
        );

        showLoadingOutput(
            "Reading file"
        );

        setInputToolsDisabled(
            true
        );

        source.value =
            "auto";

        sourceLabel.textContent =
            "Detecting language...";

        const formData =
            new FormData();

        formData.append(
            "file",
            file
        );

        formData.append(
            "targetLanguage",
            target.value
        );

        try {

            const response =
                await fetch(
                    "/api/quick-translate/file",
                    {
                        method:
                            "POST",

                        headers: {
                            "Accept":
                                "application/json"
                        },

                        body:
                            formData
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
                    "Unable to translate file"
                );
            }

            input.value =
                String(
                    data.original ||
                    ""
                );

            charCount.textContent =
                `${input.value.length} / 5000`;

            showTranslatedOutput(
                data
            );

            sourceLabel.textContent =
                data.detectedLanguage ||
                data.sourceLanguageName ||
                "Auto Detected";

            selectedFileStatus.textContent =
                `${
                    data.detectedLanguage ||
                    "Language detected"
                } • Translation completed`;

            autoStatus.innerHTML = `
                <i class="bi bi-check-circle-fill"></i>
                File translated
            `;

        } catch (error) {

            console.error(
                "QUICK FILE TRANSLATE ERROR:",
                error
            );

            loading.hidden =
                true;

            outputPlaceholder.hidden =
                false;

            autoStatus.textContent =
                "File translation failed";

            selectedFileStatus.textContent =
                "Unable to translate this file";

            setActionsEnabled(
                false
            );

            showError(
                error.message ||
                "Unable to translate the selected file."
            );

        } finally {

            setInputToolsDisabled(
                false
            );
        }
    }


    if (
        cameraBtn &&
        cameraInput
    ) {

        cameraBtn.addEventListener(
            "click",
            () => {

                closeRecorder();

                closeLiveCamera();

                cameraInput.click();
            }
        );

        cameraInput.addEventListener(
            "change",
            () => {

                translateSelectedFile(
                    cameraInput.files?.[0]
                );
            }
        );
    }


    if (
        imageBtn &&
        imageInput
    ) {

        imageBtn.addEventListener(
            "click",
            () => {

                closeRecorder();

                closeLiveCamera();

                imageInput.click();
            }
        );

        imageInput.addEventListener(
            "change",
            () => {

                translateSelectedFile(
                    imageInput.files?.[0]
                );
            }
        );
    }


    if (
        documentBtn &&
        documentInput
    ) {

        documentBtn.addEventListener(
            "click",
            () => {

                closeRecorder();

                closeLiveCamera();

                documentInput.click();
            }
        );

        documentInput.addEventListener(
            "change",
            () => {

                translateSelectedFile(
                    documentInput.files?.[0]
                );
            }
        );
    }


    if (selectedFileRemove) {

        selectedFileRemove.addEventListener(
            "click",
            () => {

                resetFileInputs();

                input.value = "";

                charCount.textContent =
                    "0 / 5000";

                sourceLabel.textContent =
                    getLanguageName(
                        source
                    );

                hideError();

                showEmptyOutput();
            }
        );
    }

    function cancelAudioTranslation() {

        /*
        * Invalidate every older voice request.
        * Even if server finishes later,
        * its result is no longer allowed
        * to update the screen.
        */
        audioTranslateRequestNumber += 1;

        audioSessionNumber += 1;

        audioTranslationRunning = false;


        if (audioTranslateController) {

            try {
                audioTranslateController.abort();
            } catch (_) {}

            audioTranslateController = null;
        }
    }

    /* =========================================
    LIVE CAMERA AUTO TRANSLATION
    ========================================= */

    function stopLiveCameraTracks() {

        if (!liveCameraStream) {
            return;
        }

        liveCameraStream
            .getTracks()
            .forEach(
                (track) => {

                    try {
                        track.stop();
                    } catch (_) {}
                }
            );

        liveCameraStream = null;
    }


    function cancelLiveCameraRequest() {

        if (liveCameraRequestController) {

            try {
                liveCameraRequestController
                    .abort();
            } catch (_) {}

            liveCameraRequestController =
                null;
        }

        liveCameraScanning =
            false;
    }


    function stopLiveCameraTimer() {

        if (liveCameraTimer) {

            clearTimeout(
                liveCameraTimer
            );

            liveCameraTimer =
                null;
        }
    }


    function closeLiveCamera() {

        liveCameraGeneration += 1;

        liveCameraRunning =
            false;

        stopLiveCameraTimer();

        cancelLiveCameraRequest();

        stopLiveCameraTracks();

        if (liveCameraVideo) {

            try {
                liveCameraVideo.pause();
            } catch (_) {}

            liveCameraVideo.srcObject =
                null;
        }

        if (liveCameraBox) {
            liveCameraBox.hidden =
                true;
        }

        if (liveCameraBtn) {

            liveCameraBtn.classList.remove(
                "is-active"
            );
        }

        if (liveCameraOverlay) {

            liveCameraOverlay.hidden =
                true;
        }

        if (liveTranslatedText) {

            liveTranslatedText.textContent =
                "";
        }

        lastLiveFrameSignature =
            "";

        lastLiveTranslatedText =
            "";

        liveCameraStatus.textContent =
            "Point camera at text";

        liveCameraBadgeText.textContent =
            "Camera stopped";
    }


    function getFrameSignature(
        canvas
    ) {

        try {

            const signatureCanvas =
                document.createElement(
                    "canvas"
                );

            signatureCanvas.width =
                16;

            signatureCanvas.height =
                16;

            const context =
                signatureCanvas
                    .getContext(
                        "2d",
                        {
                            willReadFrequently:
                                true
                        }
                    );

            context.drawImage(
                canvas,
                0,
                0,
                16,
                16
            );

            const imageData =
                context.getImageData(
                    0,
                    0,
                    16,
                    16
                ).data;

            let signature = "";

            /*
            * Coarse brightness signature.
            * Enough to determine whether
            * camera view changed materially.
            */
            for (
                let index = 0;
                index < imageData.length;
                index += 16
            ) {

                const brightness =
                    Math.round(
                        (
                            imageData[index]
                            +
                            imageData[index + 1]
                            +
                            imageData[index + 2]
                        )
                        / 3
                        / 32
                    );

                signature +=
                    brightness.toString(
                        16
                    );
            }

            return signature;

        } catch (_) {

            return String(
                Date.now()
            );
        }
    }


    function frameDifference(
        first,
        second
    ) {

        if (
            !first ||
            !second ||
            first.length !==
                second.length
        ) {

            return 1;
        }

        let differences =
            0;

        for (
            let index = 0;
            index < first.length;
            index += 1
        ) {

            if (
                first[index] !==
                second[index]
            ) {

                differences +=
                    1;
            }
        }

        return (
            differences /
            first.length
        );
    }


    function captureLiveCameraFrame() {

        if (
            !liveCameraVideo ||
            !liveCameraCanvas
        ) {

            return null;
        }

        if (
            liveCameraVideo.readyState <
            HTMLMediaElement.HAVE_CURRENT_DATA
        ) {

            return null;
        }

        const videoWidth =
            liveCameraVideo.videoWidth;

        const videoHeight =
            liveCameraVideo.videoHeight;

        if (
            !videoWidth ||
            !videoHeight
        ) {

            return null;
        }


        /*
        * Limit upload resolution.
        *
        * OCR remains readable while
        * uploads/API latency stay lower.
        */
        const maximumWidth =
            960;

        const scale =
            Math.min(
                1,
                maximumWidth /
                videoWidth
            );

        const width =
            Math.max(
                1,
                Math.round(
                    videoWidth *
                    scale
                )
            );

        const height =
            Math.max(
                1,
                Math.round(
                    videoHeight *
                    scale
                )
            );


        liveCameraCanvas.width =
            width;

        liveCameraCanvas.height =
            height;


        const context =
            liveCameraCanvas
                .getContext(
                    "2d",
                    {
                        alpha:
                            false,

                        willReadFrequently:
                            true
                    }
                );


        context.drawImage(
            liveCameraVideo,
            0,
            0,
            width,
            height
        );


        return {
            canvas:
                liveCameraCanvas,

            signature:
                getFrameSignature(
                    liveCameraCanvas
                )
        };
    }


    function canvasToJpegBlob(
        canvas
    ) {

        return new Promise(
            (resolve) => {

                canvas.toBlob(
                    (blob) => {

                        resolve(
                            blob
                        );

                    },
                    "image/jpeg",
                    0.78
                );
            }
        );
    }


    function scheduleLiveCameraScan(
        delay = 1600
    ) {

        stopLiveCameraTimer();

        if (!liveCameraRunning) {
            return;
        }

        liveCameraTimer =
            setTimeout(
                () => {

                    scanLiveCamera();

                },
                delay
            );
    }


    async function scanLiveCamera() {

        if (
            !liveCameraRunning ||
            liveCameraScanning
        ) {

            scheduleLiveCameraScan(
                900
            );

            return;
        }


        const frame =
            captureLiveCameraFrame();

        if (!frame) {

            scheduleLiveCameraScan(
                700
            );

            return;
        }


        const difference =
            frameDifference(
                lastLiveFrameSignature,
                frame.signature
            );


        /*
        * Same view = do not waste
        * another Gemini request.
        */
        if (
            lastLiveFrameSignature &&
            difference < 0.10
        ) {

            liveCameraBadgeText.textContent =
                lastLiveTranslatedText
                    ? "Translation locked"
                    : "Looking for text...";

            scheduleLiveCameraScan(
                1000
            );

            return;
        }


        lastLiveFrameSignature =
            frame.signature;


        const generation =
            liveCameraGeneration;


        liveCameraScanning =
            true;


        liveCameraBadgeText.textContent =
            "Reading text...";


        liveCameraStatus.textContent =
            "Detecting visible language...";


        const blob =
            await canvasToJpegBlob(
                frame.canvas
            );


        if (
            !blob ||
            !liveCameraRunning ||
            generation !==
                liveCameraGeneration
        ) {

            liveCameraScanning =
                false;

            return;
        }


        const formData =
            new FormData();


        formData.append(
            "file",
            blob,
            "basha-live-camera.jpg"
        );


        formData.append(
            "targetLanguage",
            target.value
        );


        cancelLiveCameraRequest();


        liveCameraScanning =
            true;


        liveCameraRequestController =
            new AbortController();


        try {

            const response =
                await fetch(
                    "/api/quick-translate/file",
                    {
                        method:
                            "POST",

                        headers: {
                            "Accept":
                                "application/json"
                        },

                        body:
                            formData,

                        signal:
                            liveCameraRequestController
                                .signal
                    }
                );


            const data =
                await response.json();


            if (
                generation !==
                    liveCameraGeneration
                ||
                !liveCameraRunning
            ) {

                return;
            }


            if (
                !response.ok ||
                !data.success
            ) {

                /*
                * No readable text is normal
                * while camera is moving.
                */
                liveCameraBadgeText.textContent =
                    "Looking for text...";

                liveCameraStatus.textContent =
                    "Point camera at readable text";

                scheduleLiveCameraScan(
                    1200
                );

                return;
            }


            const original =
                String(
                    data.original ||
                    ""
                ).trim();


            const translated =
                String(
                    data.translated ||
                    ""
                ).trim();


            if (!translated) {

                liveCameraBadgeText.textContent =
                    "Looking for text...";

                scheduleLiveCameraScan(
                    1100
                );

                return;
            }


            /*
            * Show translation directly
            * on camera view.
            */
            liveCameraOverlay.hidden =
                false;


            liveDetectedLanguage.textContent =
                `${
                    data.detectedLanguage ||
                    data.sourceLanguageName ||
                    "Auto Detected"
                } → ${
                    data.targetLanguageName ||
                    getLanguageName(
                        target
                    )
                }`;


            liveTranslatedText.textContent =
                translated;


            lastLiveTranslatedText =
                translated;


            liveCameraBadgeText.textContent =
                "Translated";


            liveCameraStatus.textContent =
                "Move camera to another text";


            /*
            * Also keep regular translator
            * boxes synchronized.
            */
            input.value =
                original;


            charCount.textContent =
                `${input.value.length} / 5000`;


            showTranslatedOutput(
                data
            );


            source.value =
                "auto";


            sourceLabel.textContent =
                data.detectedLanguage ||
                data.sourceLanguageName ||
                "Auto Detected";


        } catch (error) {

            if (
                error.name ===
                "AbortError"
            ) {

                return;
            }


            console.error(
                "LIVE CAMERA TRANSLATE ERROR:",
                error
            );


            if (
                generation ===
                    liveCameraGeneration
                &&
                liveCameraRunning
            ) {

                liveCameraBadgeText.textContent =
                    "Trying again...";

                liveCameraStatus.textContent =
                    "Keep camera steady";
            }


        } finally {

            if (
                generation ===
                liveCameraGeneration
            ) {

                liveCameraScanning =
                    false;

                liveCameraRequestController =
                    null;


                if (liveCameraRunning) {

                    scheduleLiveCameraScan(
                        1300
                    );
                }
            }
        }
    }


    async function startLiveCamera() {

        closeRecorder();

        cancelPendingTranslation();

        resetFileInputs();

        hideAudioResult();

        hideError();


        if (
            !navigator.mediaDevices ||
            !navigator.mediaDevices
                .getUserMedia
        ) {

            showError(
                "Live camera is not supported in this browser."
            );

            return;
        }


        closeLiveCamera();


        const generation =
            ++liveCameraGeneration;


        try {

            liveCameraStatus.textContent =
                "Starting camera...";

            liveCameraBadgeText.textContent =
                "Starting camera...";


            liveCameraStream =
                await navigator
                    .mediaDevices
                    .getUserMedia({

                        video: {

                            facingMode: {
                                ideal:
                                    liveCameraFacingMode
                            },

                            width: {
                                ideal:
                                    1280
                            },

                            height: {
                                ideal:
                                    720
                            }

                        },

                        audio:
                            false
                    });


            if (
                generation !==
                liveCameraGeneration
            ) {

                stopLiveCameraTracks();

                return;
            }


            liveCameraVideo.srcObject =
                liveCameraStream;


            liveCameraVideo.muted =
                true;


            await liveCameraVideo.play();


            liveCameraRunning =
                true;


            liveCameraBox.hidden =
                false;


            liveCameraBtn.classList.add(
                "is-active"
            );


            liveCameraStatus.textContent =
                "Point camera at text";


            liveCameraBadgeText.textContent =
                "Scanning automatically";


            lastLiveFrameSignature =
                "";


            lastLiveTranslatedText =
                "";


            /*
            * First scan after camera
            * exposure/focus stabilizes.
            */
            scheduleLiveCameraScan(
                900
            );


        } catch (error) {

            console.error(
                "LIVE CAMERA ERROR:",
                error
            );


            stopLiveCameraTracks();


            liveCameraRunning =
                false;


            liveCameraBox.hidden =
                true;


            liveCameraBtn.classList.remove(
                "is-active"
            );


            if (
                error.name ===
                    "NotAllowedError"
                ||
                error.name ===
                    "PermissionDeniedError"
            ) {

                showError(
                    "Camera permission was blocked. Please allow camera access in browser settings."
                );

            } else {

                showError(
                    "Unable to open camera. Please check camera access and try again."
                );
            }
        }
    }


    async function switchLiveCamera() {

        if (!liveCameraRunning) {
            return;
        }


        liveCameraFacingMode =
            liveCameraFacingMode ===
                "environment"
                ? "user"
                : "environment";


        closeLiveCamera();


        await startLiveCamera();
    }


    /* LIVE CAMERA EVENTS */

    if (liveCameraBtn) {

        liveCameraBtn.addEventListener(
            "click",
            () => {

                if (
                    liveCameraRunning
                ) {

                    closeLiveCamera();

                } else {

                    startLiveCamera();
                }
            }
        );
    }


    if (liveCameraClose) {

        liveCameraClose.addEventListener(
            "click",
            closeLiveCamera
        );
    }


    if (liveCameraSwitch) {

        liveCameraSwitch.addEventListener(
            "click",
            switchLiveCamera
        );
    }


    /* =========================================
       AUDIO RECORDER
    ========================================= */

    function getSupportedAudioMimeType() {

        if (
            typeof MediaRecorder ===
            "undefined"
        ) {
            return "";
        }

        const candidates = [
            "audio/webm;codecs=opus",
            "audio/webm",
            "audio/mp4",
            "audio/ogg;codecs=opus"
        ];

        for (
            const mimeType
            of candidates
        ) {

            if (
                MediaRecorder
                    .isTypeSupported(
                        mimeType
                    )
            ) {
                return mimeType;
            }
        }

        return "";
    }


    function extensionFromMimeType(
        mimeType
    ) {

        mimeType =
            String(
                mimeType || ""
            ).toLowerCase();

        if (
            mimeType.includes(
                "mp4"
            )
        ) {
            return "m4a";
        }

        if (
            mimeType.includes(
                "ogg"
            )
        ) {
            return "ogg";
        }

        if (
            mimeType.includes(
                "wav"
            )
        ) {
            return "wav";
        }

        return "webm";
    }


    function formatTime(seconds) {

        const minutes =
            Math.floor(
                seconds / 60
            );

        const remaining =
            seconds % 60;

        return (
            String(minutes)
                .padStart(
                    2,
                    "0"
                )
            +
            ":"
            +
            String(remaining)
                .padStart(
                    2,
                    "0"
                )
        );
    }


    function stopTimer() {

        if (recordingTimer) {

            clearInterval(
                recordingTimer
            );

            recordingTimer =
                null;
        }
    }


    function stopMicrophoneTracks() {

        if (!microphoneStream) {
            return;
        }

        microphoneStream
            .getTracks()
            .forEach(
                (track) => {

                    try {
                        track.stop();
                    } catch (_) {}
                }
            );

        microphoneStream =
            null;
    }


    function resetRecorderButtons() {

        recordStart.hidden =
            false;

        recordStop.hidden =
            true;

        recorderBox.classList.remove(
            "is-recording"
        );
    }


    function stopRecordingImmediately(
        processRecording = true
    ) {

        stopTimer();

        if (
            mediaRecorder &&
            mediaRecorder.state !==
                "inactive"
        ) {

            mediaRecorder
                .datasetProcessRecording =
                    processRecording
                        ? "true"
                        : "false";

            try {
                mediaRecorder.stop();
            } catch (_) {}
        }

        stopMicrophoneTracks();

        resetRecorderButtons();
    }


    function openRecorder() {

        closeLiveCamera();

        cancelPendingTranslation();

        cancelAudioTranslation();

        resetFileInputs();

        hideError();

        hideAudioResult();

        latestAudioBlob = null;

        audioChunks = [];

        recordingSeconds = 0;

        recorderBox.hidden = false;

        audioBtn.classList.add(
            "is-active"
        );

        recorderBox.classList.remove(
            "is-recording"
        );

        recorderTitle.textContent =
            "Voice Translation";

        recorderStatus.textContent =
            "Tap Start and speak naturally";

        recordTime.textContent =
            "00:00";

        recordStart.hidden = false;

        recordStart.disabled = false;

        recordStart.innerHTML = `
            <i class="bi bi-mic-fill"></i>
            <span>Start Recording</span>
        `;

        recordStop.hidden = true;

        /*
        * New voice session should start
        * with a clean translator result.
        */
        input.value = "";

        charCount.textContent =
            "0 / 5000";

        source.value = "auto";

        sourceLabel.textContent =
            "Auto Detect";

        showEmptyOutput();
    }

    function closeRecorder() {

        /*
        * First invalidate current
        * translation request.
        */
        cancelAudioTranslation();

        stopTimer();


        /*
        * Stop active recorder without
        * sending it for translation.
        */
        if (
            mediaRecorder &&
            mediaRecorder.state !==
                "inactive"
        ) {

            mediaRecorder
                .datasetProcessRecording =
                    "false";

            try {
                mediaRecorder.stop();
            } catch (_) {}
        }


        stopMicrophoneTracks();


        mediaRecorder = null;

        audioChunks = [];

        latestAudioBlob = null;

        recordingSeconds = 0;


        recorderBox.classList.remove(
            "is-recording"
        );

        recorderBox.hidden = true;


        audioBtn.classList.remove(
            "is-active"
        );


        recordStart.hidden = false;

        recordStart.disabled = false;

        recordStart.innerHTML = `
            <i class="bi bi-mic-fill"></i>
            <span>Start Recording</span>
        `;

        recordStop.hidden = true;


        recorderTitle.textContent =
            "Voice Translation";

        recorderStatus.textContent =
            "Tap Start and speak naturally";

        recordTime.textContent =
            "00:00";


        /*
        * Completely clear old voice
        * translation from the boxes.
        */
        input.value = "";

        charCount.textContent =
            "0 / 5000";

        source.value =
            "auto";

        sourceLabel.textContent =
            "Auto Detect";

        hideAudioResult();

        hideError();

        showEmptyOutput();
    }

    async function startRecording() {

        /*
        * Every recording is a completely
        * new voice translation session.
        */
        cancelPendingTranslation();

        cancelAudioTranslation();

        hideError();

        hideAudioResult();

        resetFileInputs();

        latestAudioBlob = null;

        audioChunks = [];

        input.value = "";

        charCount.textContent =
            "0 / 5000";

        latestTranslation = "";

        translatedText.textContent = "";

        translatedText.hidden = true;

        outputPlaceholder.hidden = false;

        setActionsEnabled(false);

        source.value = "auto";

        sourceLabel.textContent =
            "Listening...";

        recorderTitle.textContent =
            "Starting microphone...";

        recorderStatus.textContent =
            "Please wait";

        recordStart.disabled = true;

        if (
            !navigator.mediaDevices ||
            !navigator.mediaDevices
                .getUserMedia
        ) {

            showError(
                "Microphone recording is not supported in this browser."
            );

            return;
        }

        if (
            typeof MediaRecorder ===
            "undefined"
        ) {

            showError(
                "Audio recording is not supported in this browser."
            );

            return;
        }

        try {

            microphoneStream =
                await navigator
                    .mediaDevices
                    .getUserMedia({
                        audio: {
                            echoCancellation:
                                true,

                            noiseSuppression:
                                true,

                            autoGainControl:
                                true
                        }
                    });

            const mimeType =
                getSupportedAudioMimeType();

            const options =
                mimeType
                    ? {
                        mimeType:
                            mimeType
                    }
                    : undefined;

            mediaRecorder =
                new MediaRecorder(
                    microphoneStream,
                    options
                );

            audioChunks = [];

            const activeRecorder =
                mediaRecorder;

            activeRecorder
                .datasetProcessRecording =
                    "true";

            activeRecorder.addEventListener(
                "dataavailable",
                (event) => {

                    if (
                        event.data &&
                        event.data.size > 0
                    ) {

                        audioChunks.push(
                            event.data
                        );
                    }
                }
            );


            activeRecorder.addEventListener(
                "stop",
                async () => {

                    const shouldProcess =
                        activeRecorder
                            .datasetProcessRecording
                        !== "false";

                    stopMicrophoneTracks();

                    if (!shouldProcess) {

                        audioChunks = [];

                        return;
                    }

                    if (
                        audioChunks.length ===
                        0
                    ) {

                        showError(
                            "No audio was captured. Please try again."
                        );

                        return;
                    }

                    const recordedMimeType =
                        activeRecorder.mimeType ||
                        mimeType ||
                        "audio/webm";

                    latestAudioBlob =
                        new Blob(
                            audioChunks,
                            {
                                type:
                                    recordedMimeType
                            }
                        );

                    const extension =
                        extensionFromMimeType(
                            recordedMimeType
                        );

                    latestAudioFilename =
                        `basha-recording.${extension}`;

                    audioChunks = [];

                    await translateRecordedAudio(
                        latestAudioBlob,
                        latestAudioFilename
                    );
                }
            );


            activeRecorder.start(
                250
            );

            recordStart.disabled = false;

            recorderBox.classList.add(
                "is-recording"
            );

            recordStart.hidden =
                true;

            recordStop.hidden =
                false;

            recorderTitle.textContent =
                "Listening...";

            recorderStatus.textContent =
                "Speak clearly. Tap Stop when finished.";

            recordingSeconds =
                0;

            recordTime.textContent =
                "00:00";

            recordingTimer =
                setInterval(
                    () => {

                        recordingSeconds +=
                            1;

                        recordTime.textContent =
                            formatTime(
                                recordingSeconds
                            );

                        /*
                         * Production safety:
                         * auto stop after 2 minutes.
                         */
                        if (
                            recordingSeconds >=
                            120
                        ) {

                            stopRecordingImmediately(
                                true
                            );
                        }

                    },
                    1000
                );

        } catch (error) {

            console.error(
                "MICROPHONE ERROR:",
                error
            );

            stopMicrophoneTracks();

            resetRecorderButtons();

            if (
                error.name ===
                    "NotAllowedError"
                ||
                error.name ===
                    "PermissionDeniedError"
            ) {

                showError(
                    "Microphone permission was blocked. Please allow microphone access in your browser settings."
                );

            } else {

                showError(
                    "Unable to start microphone. Please check microphone access and try again."
                );
            }
        }
    }


    async function translateRecordedAudio(
        audioBlob,
        fileName
    ) {

        if (
            !audioBlob ||
            !audioBlob.size
        ) {

            showError(
                "Recorded audio is empty."
            );

            return;
        }


        /*
        * Cancel only an older AUDIO request.
        * Do not destroy this audio blob.
        */
        cancelPendingTranslation();

        if (audioTranslateController) {

            try {
                audioTranslateController.abort();
            } catch (_) {}
        }


        const requestNumber =
            ++audioTranslateRequestNumber;

        const sessionNumber =
            audioSessionNumber;


        audioTranslateController =
            new AbortController();


        audioTranslationRunning =
            true;


        hideError();

        hideAudioResult();


        showLoadingOutput(
            "Processing voice"
        );

        setInputToolsDisabled(
            true
        );

        recorderBox.classList.remove(
            "is-recording"
        );

        recorderTitle.textContent =
            "Translating voice...";

        recorderStatus.textContent =
            "Understanding your recording...";

        source.value =
            "auto";

        sourceLabel.textContent =
            "Detecting spoken language...";

        recordStart.hidden =
            false;

        recordStart.disabled =
            true;

        recordStart.innerHTML = `
            <span class="spinner-border spinner-border-sm"></span>
            <span>Processing...</span>
        `;

        recordStop.hidden =
            true;

        const formData =
            new FormData();

        formData.append(
            "audio",
            audioBlob,
            fileName
        );

        formData.append(
            "target_language_code",
            target.value
        );

        formData.append(
            "target_language_name",
            getLanguageName(
                target
            )
        );

        try {

            const response =
                await fetch(
                    "/audio/translate-preview",
                    {
                        method:
                            "POST",

                        headers: {
                            "Accept":
                                "application/json"
                        },

                        body:
                            formData,

                        signal:
                            audioTranslateController
                                .signal
                    }
                );

            const data =
                await response.json();

            /*
            * CRITICAL:
            *
            * User may have clicked Close
            * while Gemini was processing.
            *
            * Never allow that old response
            * to touch the new UI.
            */
            if (
                requestNumber !==
                    audioTranslateRequestNumber
                ||
                sessionNumber !==
                    audioSessionNumber
                ||
                recorderBox.hidden
            ) {

                return;
            }

            if (
                !response.ok ||
                !data.success
            ) {

                throw new Error(
                    data.error ||
                    "Unable to translate voice"
                );
            }

            input.value =
                String(
                    data.original ||
                    ""
                );

            charCount.textContent =
                `${input.value.length} / 5000`;

            showTranslatedOutput(
                data
            );

            sourceLabel.textContent =
                data.detectedLanguage ||
                data.sourceLanguageName ||
                "Auto Detected";

            recorderTitle.textContent =
                "Translation complete";

            recordTime.textContent =
                "Done";

            recorderStatus.textContent =
                `${
                    data.detectedLanguage ||
                    "Language detected"
                } → ${
                    data.targetLanguageName ||
                    getLanguageName(target)
                }`;

            autoStatus.innerHTML = `
                <i class="bi bi-check-circle-fill"></i>
                Voice translated
            `;

            if (
                data.translatedAudioAvailable &&
                data.translatedAudioData
            ) {

                translatedAudio.src =
                    data.translatedAudioData;

                translatedAudio.load();

                detectedLanguage.textContent =
                    `${
                        data.detectedLanguage ||
                        "Auto Detected"
                    } → ${
                        data.targetLanguageName ||
                        getLanguageName(target)
                    }`;

                audioResult.hidden =
                    false;

            } else {

                hideAudioResult();
            }

        } catch (error) {

            /*
            * Abort is intentional when
            * user closes/restarts recorder.
            */
            if (
                error.name ===
                "AbortError"
            ) {

                return;
            }

            /*
            * Ignore errors belonging to
            * an old voice session.
            */
            if (
                requestNumber !==
                    audioTranslateRequestNumber
                ||
                sessionNumber !==
                    audioSessionNumber
            ) {

                return;
            }

            console.error(
                "VOICE TRANSLATION ERROR:",
                error
            );

            loading.hidden =
                true;

            outputPlaceholder.hidden =
                false;

            recorderTitle.textContent =
                "Translation failed";

            recorderStatus.textContent =
                "Please try recording again";

            autoStatus.textContent =
                "Voice translation failed";

            showError(
                error.message ||
                "Unable to translate recorded voice."
            );

            setActionsEnabled(
                false
            );

        } finally {

            /*
            * Only the current request may
            * reset current UI.
            */
            if (
                requestNumber ===
                    audioTranslateRequestNumber
                &&
                sessionNumber ===
                    audioSessionNumber
            ) {

                audioTranslationRunning =
                    false;


                audioTranslateController =
                    null;


                setInputToolsDisabled(
                    false
                );


                stopMicrophoneTracks();


                if (!recorderBox.hidden) {

                    resetRecorderButtons();

                    recordStart.disabled =
                        false;

                    recordStart.innerHTML = `
                        <i class="bi bi-mic-fill"></i>
                        <span>Start Recording</span>
                    `;
                }
            }
        }
    }

    /* =========================================
    AUDIO BUTTON EVENTS
    ========================================= */

    if (
        audioBtn &&
        recorderBox
    ) {

        audioBtn.addEventListener(
            "click",
            () => {

                if (
                    recorderBox.hidden
                ) {

                    openRecorder();

                } else {

                    closeRecorder();
                }
            }
        );
    }


    if (recordStart) {

        recordStart.addEventListener(
            "click",
            () => {

                if (
                    audioTranslationRunning
                ) {
                    return;
                }

                startRecording();
            }
        );
    }

    if (recordStop) {

        recordStop.addEventListener(
            "click",
            () => {

                recorderTitle.textContent =
                    "Recording stopped";

                recorderStatus.textContent =
                    "Preparing translation...";

                stopRecordingImmediately(
                    true
                );
            }
        );
    }


    if (recordCancel) {

        recordCancel.addEventListener(
            "click",
            () => {

                closeRecorder();

            }
        );
    }


    /* =========================================
       CARD TOGGLE
    ========================================= */

    toggle.addEventListener(
        "click",
        () => {

            if (collapse.hidden) {

                openCard();

            } else {

                stopRecordingImmediately(
                    false
                );

                closeLiveCamera();

                closeCard();
            }
        }
    );


    /* =========================================
       TEXT AUTO TRANSLATION
    ========================================= */

    function scheduleTranslation(
        delay = 700
    ) {

        cancelPendingTranslation();

        hideError();

        hideAudioResult();

        const text =
            input.value.trim();

        charCount.textContent =
            `${input.value.length} / 5000`;

        sourceLabel.textContent =
            getLanguageName(
                source
            );

        if (!text) {

            showEmptyOutput();

            return;
        }

        autoStatus.textContent =
            "Waiting for typing...";

        translationTimer =
            setTimeout(
                () => {

                    translateTextAutomatically();

                },
                delay
            );
    }


    async function translateTextAutomatically() {

        const text =
            input.value.trim();

        if (!text) {

            showEmptyOutput();

            return;
        }

        const requestNumber =
            ++translationRequestNumber;

        activeController =
            new AbortController();

        hideError();

        showLoadingOutput(
            "Translating"
        );

        try {

            const response =
                await fetch(
                    "/api/quick-translate",
                    {
                        method:
                            "POST",

                        headers: {
                            "Content-Type":
                                "application/json",

                            "Accept":
                                "application/json"
                        },

                        body:
                            JSON.stringify({
                                text:
                                    text,

                                sourceLanguage:
                                    source.value,

                                targetLanguage:
                                    target.value
                            }),

                        signal:
                            activeController.signal
                    }
                );

            const data =
                await response.json();

            if (
                requestNumber !==
                translationRequestNumber
            ) {
                return;
            }

            if (
                !response.ok ||
                !data.success
            ) {

                throw new Error(
                    data.error ||
                    "Translation failed"
                );
            }

            showTranslatedOutput(
                data
            );

        } catch (error) {

            if (
                error.name ===
                "AbortError"
            ) {
                return;
            }

            console.error(
                "QUICK TRANSLATE ERROR:",
                error
            );

            loading.hidden =
                true;

            outputPlaceholder.hidden =
                false;

            autoStatus.textContent =
                "Translation failed";

            setActionsEnabled(
                false
            );

            showError(
                error.message ||
                "Unable to translate."
            );

        } finally {

            activeController =
                null;
        }
    }


    input.addEventListener(
        "input",
        () => {

            latestAudioBlob =
                null;

            scheduleTranslation(
                700
            );
        }
    );


    source.addEventListener(
        "change",
        () => {

            scheduleTranslation(
                150
            );
        }
    );


    target.addEventListener(
        "change",
        () => {

            if (liveCameraRunning) {

                lastLiveFrameSignature =
                    "";

                lastLiveTranslatedText =
                    "";

                liveCameraOverlay.hidden =
                    true;

                liveCameraBadgeText.textContent =
                    "Language changed";

                liveCameraStatus.textContent =
                    "Scanning again...";

                scheduleLiveCameraScan(
                    250
                );

                return;
            }

            const activeFile =
                cameraInput?.files?.[0]
                ||
                imageInput?.files?.[0]
                ||
                documentInput?.files?.[0];


            if (activeFile) {

                translateSelectedFile(
                    activeFile
                );

                return;
            }


            /*
            * Do not automatically resend
            * an old voice recording.
            */
            if (
                latestAudioBlob ||
                audioTranslationRunning
            ) {

                cancelAudioTranslation();

                latestAudioBlob =
                    null;

                hideAudioResult();

                input.value =
                    "";

                charCount.textContent =
                    "0 / 5000";

                source.value =
                    "auto";

                sourceLabel.textContent =
                    "Auto Detect";

                recorderTitle.textContent =
                    "Voice Translation";

                recorderStatus.textContent =
                    "Target changed. Record again.";

                recordTime.textContent =
                    "00:00";

                showEmptyOutput();

                return;
            }


            scheduleTranslation(
                150
            );

        }
    );


    /* =========================================
       CLEAR
    ========================================= */

    clearBtn.addEventListener(
        "click",
        () => {

            cancelPendingTranslation();

            stopRecordingImmediately(
                false
            );

            closeLiveCamera();

            resetFileInputs();

            latestAudioBlob =
                null;

            input.value = "";

            charCount.textContent =
                "0 / 5000";

            sourceLabel.textContent =
                getLanguageName(
                    source
                );

            recorderTitle.textContent =
                "Voice Translation";

            recorderStatus.textContent =
                "Tap Start and speak naturally";

            recordTime.textContent =
                "00:00";

            hideError();

            showEmptyOutput();

            input.focus();
        }
    );


    /* =========================================
       SWAP
    ========================================= */

    swap.addEventListener(
        "click",
        () => {

            if (
                source.value ===
                "auto"
            ) {

                source.value =
                    target.value;

                target.value =
                    "en";

            } else {

                const oldSource =
                    source.value;

                source.value =
                    target.value;

                target.value =
                    oldSource;
            }

            if (
                latestAudioBlob ||
                audioTranslationRunning
            ) {

                cancelAudioTranslation();

                latestAudioBlob = null;

                hideAudioResult();

                input.value = "";

                charCount.textContent =
                    "0 / 5000";

                source.value =
                    "auto";

                sourceLabel.textContent =
                    "Auto Detect";

                recorderTitle.textContent =
                    "Voice Translation";

                recorderStatus.textContent =
                    "Languages changed. Record again.";

                recordTime.textContent =
                    "00:00";

                showEmptyOutput();

                return;
            }
            

            if (latestTranslation) {

                const oldInput =
                    input.value;

                input.value =
                    latestTranslation;

                latestTranslation =
                    oldInput.trim();

                charCount.textContent =
                    `${input.value.length} / 5000`;
            }

            scheduleTranslation(
                100
            );
        }
    );


    /* =========================================
       COPY
    ========================================= */

    async function copyTranslation() {

        if (!latestTranslation) {
            return;
        }

        try {

            await navigator
                .clipboard
                .writeText(
                    latestTranslation
                );

            copyActionBtn.innerHTML = `
                <i class="bi bi-check-lg"></i>
                Copied
            `;

            copyBtn.innerHTML = `
                <i class="bi bi-check-lg"></i>
            `;

            setTimeout(
                () => {

                    copyActionBtn.innerHTML = `
                        <i class="bi bi-copy"></i>
                        Copy
                    `;

                    copyBtn.innerHTML = `
                        <i class="bi bi-copy"></i>
                    `;

                },
                1200
            );

        } catch (_) {

            alert(
                "Unable to copy text."
            );
        }
    }


    copyBtn.addEventListener(
        "click",
        copyTranslation
    );

    copyActionBtn.addEventListener(
        "click",
        copyTranslation
    );


    /* =========================================
       CONTACT POPUP
    ========================================= */

    const contactModal =
        document.getElementById(
            "qtContactModal"
        );

    const contactBackdrop =
        document.getElementById(
            "qtContactBackdrop"
        );

    const contactClose =
        document.getElementById(
            "qtContactClose"
        );

    const contactSearch =
        document.getElementById(
            "qtContactSearch"
        );

    const contactCount =
        document.getElementById(
            "qtContactCount"
        );

    const contactLoading =
        document.getElementById(
            "qtContactLoading"
        );

    const contactEmpty =
        document.getElementById(
            "qtContactEmpty"
        );

    const contactList =
        document.getElementById(
            "qtContactList"
        );


    const contactModalReady =
        contactModal &&
        contactBackdrop &&
        contactClose &&
        contactSearch &&
        contactCount &&
        contactLoading &&
        contactEmpty &&
        contactList;


    let quickContacts = [];

    let contactsLoaded =
        false;


    function openContactModal() {

        if (
            !latestTranslation ||
            !contactModalReady
        ) {
            return;
        }

        contactModal.hidden =
            false;

        document.body.style.overflow =
            "hidden";

        setTimeout(
            () => {

                contactSearch.focus();

            },
            100
        );

        if (!contactsLoaded) {

            loadQuickContacts();
        }
    }


    function closeContactModal() {

        contactModal.hidden =
            true;

        document.body.style.overflow =
            "";

        contactSearch.value =
            "";

        renderQuickContacts(
            quickContacts
        );
    }


    function buildContactAvatar(
        contact
    ) {

        const profilePic =
            escapeHtml(
                contact.profilePic ||
                ""
            );

        const firstLetter =
            escapeHtml(
                String(
                    contact.name ||
                    "U"
                )
                    .charAt(0)
                    .toUpperCase()
            );

        if (profilePic) {

            return `
                <div class="qt-contact-avatar">

                    <img src="${profilePic}"
                         alt="${escapeHtml(
                            contact.name ||
                            "User"
                         )}"
                         loading="lazy">

                </div>
            `;
        }

        return `
            <div class="qt-contact-avatar">
                ${firstLetter}
            </div>
        `;
    }


    function renderQuickContacts(
        contacts
    ) {

        contactList.innerHTML =
            "";

        if (
            !Array.isArray(
                contacts
            )
            ||
            contacts.length ===
                0
        ) {

            contactEmpty.hidden =
                false;

            contactCount.textContent =
                "0 contacts";

            return;
        }

        contactEmpty.hidden =
            true;

        contactCount.textContent =
            `${contacts.length} contact${
                contacts.length === 1
                    ? ""
                    : "s"
            }`;

        contactList.innerHTML =
            contacts.map(
                (contact) => {

                    return `
                        <button type="button"
                                class="qt-contact-item"
                                data-mobile="${escapeHtml(
                                    contact.mobile
                                )}">

                            ${buildContactAvatar(
                                contact
                            )}

                            <div class="qt-contact-info">

                                <div class="qt-contact-name">
                                    ${escapeHtml(
                                        contact.name ||
                                        "User"
                                    )}
                                </div>

                                <div class="qt-contact-meta">

                                    ${escapeHtml(
                                        contact.mobile ||
                                        ""
                                    )}

                                    ${
                                        contact.languageName
                                            ? ` • ${escapeHtml(
                                                contact.languageName
                                            )}`
                                            : ""
                                    }

                                </div>

                            </div>

                            <span class="qt-contact-send-icon">
                                <i class="bi bi-send-fill"></i>
                            </span>

                        </button>
                    `;
                }
            ).join("");

        contactList
            .querySelectorAll(
                ".qt-contact-item"
            )
            .forEach(
                (button) => {

                    button.addEventListener(
                        "click",
                        () => {

                            sendTranslationToContact(
                                button
                            );
                        }
                    );
                }
            );
    }


    async function loadQuickContacts() {

        contactLoading.hidden =
            false;

        contactEmpty.hidden =
            true;

        contactList.innerHTML =
            "";

        contactCount.textContent =
            "";

        try {

            const response =
                await fetch(
                    "/api/quick-translate/contacts",
                    {
                        headers: {
                            "Accept":
                                "application/json"
                        },

                        cache:
                            "no-store"
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
                    "Unable to load contacts"
                );
            }

            quickContacts =
                Array.isArray(
                    data.items
                )
                    ? data.items
                    : [];

            contactsLoaded =
                true;

            renderQuickContacts(
                quickContacts
            );

        } catch (error) {

            console.error(
                "QUICK CONTACTS ERROR:",
                error
            );

            contactEmpty.hidden =
                false;

            contactEmpty.innerHTML = `
                <i class="bi bi-exclamation-circle"></i>

                <strong>
                    Unable to load contacts
                </strong>
            `;

        } finally {

            contactLoading.hidden =
                true;
        }
    }


    async function sendTranslationToContact(
        button
    ) {

        const receiverMobile =
            String(
                button.dataset.mobile ||
                ""
            ).trim();

        if (
            !receiverMobile ||
            !latestTranslation
        ) {
            return;
        }

        const oldContent =
            button.innerHTML;

        button.disabled =
            true;

        const icon =
            button.querySelector(
                ".qt-contact-send-icon"
            );

        if (icon) {

            icon.innerHTML = `
                <span class="spinner-border spinner-border-sm"></span>
            `;
        }

        try {

            const formData =
                new FormData();

            formData.append(
                "receiver_mobile",
                receiverMobile
            );

            formData.append(
                "message",
                latestTranslation
            );

            const response =
                await fetch(
                    "/send-message",
                    {
                        method:
                            "POST",

                        body:
                            formData
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
                    "Unable to send message"
                );
            }

            button.classList.add(
                "is-sent"
            );

            if (icon) {

                icon.innerHTML =
                    '<i class="bi bi-check-lg"></i>';
            }

            const name =
                button.querySelector(
                    ".qt-contact-name"
                );

            if (name) {

                name.textContent =
                    `${name.textContent} — Sent`;
            }

            setTimeout(
                () => {

                    closeContactModal();

                },
                900
            );

        } catch (error) {

            console.error(
                "QUICK TRANSLATE SEND ERROR:",
                error
            );

            button.disabled =
                false;

            button.innerHTML =
                oldContent;

            alert(
                error.message ||
                "Unable to send translated text"
            );
        }
    }


    sendBtn.addEventListener(
        "click",
        openContactModal
    );


    if (contactModalReady) {

        contactSearch.addEventListener(
            "input",
            () => {

                const query =
                    contactSearch.value
                        .trim()
                        .toLowerCase();

                const filteredContacts =
                    quickContacts.filter(
                        (contact) => {

                            const searchValue = `
                                ${contact.name || ""}
                                ${contact.mobile || ""}
                                ${contact.languageName || ""}
                            `.toLowerCase();

                            return searchValue
                                .includes(
                                    query
                                );
                        }
                    );

                renderQuickContacts(
                    filteredContacts
                );
            }
        );


        contactClose.addEventListener(
            "click",
            closeContactModal
        );


        contactBackdrop.addEventListener(
            "click",
            closeContactModal
        );
    }


    document.addEventListener(
        "keydown",
        (event) => {

            if (
                contactModalReady &&
                event.key ===
                    "Escape" &&
                !contactModal.hidden
            ) {

                closeContactModal();
            }
        }
    );


    /* =========================================
       MOBILE / PAGE CLEANUP
    ========================================= */

    function cleanupMedia() {

        stopRecordingImmediately(
            false
        );

        stopMicrophoneTracks();

        closeLiveCamera();
    }


    window.addEventListener(
        "pagehide",
        cleanupMedia
    );


    document.addEventListener(
        "visibilitychange",
        () => {

            if (
                document.hidden &&
                mediaRecorder &&
                mediaRecorder.state !==
                    "inactive"
            ) {

                stopRecordingImmediately(
                    false
                );

                recorderStatus.textContent =
                    "Recording stopped because the app moved to background.";
            }

            if (
                document.hidden &&
                liveCameraRunning
            ) {

                closeLiveCamera();
            }
        }
    );


    /* =========================================
       INITIAL STATE
    ========================================= */

    charCount.textContent =
        `${input.value.length} / 5000`;

    sourceLabel.textContent =
        getLanguageName(
            source
        );

    showEmptyOutput();

    /*
     * Translator must be open immediately
     * when Home loads.
     */
    openCard();

});