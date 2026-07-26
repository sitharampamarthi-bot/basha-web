document.addEventListener("DOMContentLoaded", () => {

    const card =
        document.getElementById("quickTranslateCard");

    if (!card) {
        return;
    }


    /* =========================================
       MAIN ELEMENTS
    ========================================= */

    const toggle =
        document.getElementById("qtToggle");

    const collapse =
        document.getElementById("qtCollapse");

    const source =
        document.getElementById("qtSourceLanguage");

    const target =
        document.getElementById("qtTargetLanguage");

    const swap =
        document.getElementById("qtSwapBtn");

    const input =
        document.getElementById("qtInput");

    const charCount =
        document.getElementById("qtCharCount");

    const sourceLabel =
        document.getElementById("qtSourceLabel");

    const resultLanguage =
        document.getElementById("qtResultLanguage");

    const resultCount =
        document.getElementById("qtResultCount");

    const clearBtn =
        document.getElementById("qtClearBtn");

    const errorBox =
        document.getElementById("qtError");

    const outputPlaceholder =
        document.getElementById("qtOutputPlaceholder");

    const loading =
        document.getElementById("qtLoading");

    const translatedText =
        document.getElementById("qtTranslatedText");

    const autoStatus =
        document.getElementById("qtAutoStatus");

    const copyBtn =
        document.getElementById("qtCopyBtn");

    const copyActionBtn =
        document.getElementById("qtCopyActionBtn");

    const sendBtn =
        document.getElementById("qtSendBtn");


    let latestTranslation = "";
    let translationTimer = null;
    let activeController = null;
    let translationRequestNumber = 0;


    /* =========================================
       HELPERS
    ========================================= */

    function escapeHtml(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }


    function getLanguageName(selectElement) {
        const selectedOption =
            selectElement.options[
                selectElement.selectedIndex
            ];

        return selectedOption
            ? selectedOption.textContent.trim()
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


    function setActionsEnabled(enabled) {
        copyBtn.disabled = !enabled;
        copyActionBtn.disabled = !enabled;
        sendBtn.disabled = !enabled;
    }


    function hideError() {
        errorBox.hidden = true;
        errorBox.textContent = "";
    }


    function showError(message) {
        errorBox.textContent =
            message || "Unable to translate.";

        errorBox.hidden = false;
    }


    function showEmptyOutput() {
        latestTranslation = "";

        loading.hidden = true;
        translatedText.hidden = true;
        translatedText.textContent = "";

        outputPlaceholder.hidden = false;

        resultCount.textContent =
            "0 characters";

        resultLanguage.textContent =
            "Select languages and start typing";

        autoStatus.textContent =
            "Auto translate";

        setActionsEnabled(false);
    }


    function showLoadingOutput() {
        outputPlaceholder.hidden = true;
        translatedText.hidden = true;
        loading.hidden = false;

        autoStatus.innerHTML = `
            <span class="spinner-border spinner-border-sm"></span>
            Translating
        `;

        setActionsEnabled(false);
    }


    function showTranslatedOutput(data) {
        latestTranslation =
            String(data.translated || "").trim();

        loading.hidden = true;
        outputPlaceholder.hidden = true;

        translatedText.textContent =
            latestTranslation;

        translatedText.hidden = false;

        resultLanguage.textContent =
            `${data.sourceLanguageName} → ${data.targetLanguageName}`;

        sourceLabel.textContent =
            data.sourceLanguageName || getLanguageName(source);

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
            Boolean(latestTranslation)
        );
    }


    function cancelPendingTranslation() {
        clearTimeout(translationTimer);

        translationTimer = null;

        if (activeController) {
            activeController.abort();
            activeController = null;
        }
    }


    /* =========================================
       CARD TOGGLE
    ========================================= */

    toggle.addEventListener("click", () => {
        collapse.hidden
            ? openCard()
            : closeCard();
    });


    /* =========================================
       AUTO TRANSLATION
    ========================================= */

    function scheduleTranslation(delay = 700) {
        cancelPendingTranslation();

        hideError();

        const text = input.value.trim();

        charCount.textContent =
            `${input.value.length} / 5000`;

        sourceLabel.textContent =
            getLanguageName(source);

        if (!text) {
            showEmptyOutput();
            return;
        }

        autoStatus.textContent =
            "Waiting for typing...";

        translationTimer = setTimeout(() => {
            translateTextAutomatically();
        }, delay);
    }


    async function translateTextAutomatically() {
        const text = input.value.trim();

        if (!text) {
            showEmptyOutput();
            return;
        }

        const requestNumber =
            ++translationRequestNumber;

        activeController =
            new AbortController();

        hideError();
        showLoadingOutput();

        try {
            const response = await fetch(
                "/api/quick-translate",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "Accept":
                            "application/json"
                    },

                    body: JSON.stringify({
                        text: text,
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

            if (!response.ok || !data.success) {
                throw new Error(
                    data.error ||
                    "Translation failed"
                );
            }

            showTranslatedOutput(data);

        } catch (error) {
            if (error.name === "AbortError") {
                return;
            }

            console.error(
                "QUICK TRANSLATE ERROR:",
                error
            );

            loading.hidden = true;

            outputPlaceholder.hidden = false;

            autoStatus.textContent =
                "Translation failed";

            setActionsEnabled(false);

            showError(
                error.message ||
                "Unable to translate."
            );

        } finally {
            activeController = null;
        }
    }


    input.addEventListener("input", () => {
        scheduleTranslation(700);
    });


    source.addEventListener("change", () => {
        scheduleTranslation(150);
    });


    target.addEventListener("change", () => {
        scheduleTranslation(150);
    });


    /* =========================================
       CLEAR
    ========================================= */

    clearBtn.addEventListener("click", () => {
        cancelPendingTranslation();

        input.value = "";

        charCount.textContent =
            "0 / 5000";

        sourceLabel.textContent =
            getLanguageName(source);

        hideError();
        showEmptyOutput();

        input.focus();
    });


    /* =========================================
       SWAP
    ========================================= */

    swap.addEventListener("click", () => {

        if (source.value === "auto") {
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

        scheduleTranslation(100);
    });


    /* =========================================
       COPY
    ========================================= */

    async function copyTranslation() {
        if (!latestTranslation) {
            return;
        }

        try {
            await navigator.clipboard.writeText(
                latestTranslation
            );

            copyActionBtn.innerHTML = `
                <i class="bi bi-check-lg"></i>
                Copied
            `;

            copyBtn.innerHTML = `
                <i class="bi bi-check-lg"></i>
            `;

            setTimeout(() => {
                copyActionBtn.innerHTML = `
                    <i class="bi bi-copy"></i>
                    Copy
                `;

                copyBtn.innerHTML = `
                    <i class="bi bi-copy"></i>
                `;
            }, 1200);

        } catch (error) {
            alert("Unable to copy text.");
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
        document.getElementById("qtContactModal");

    const contactBackdrop =
        document.getElementById("qtContactBackdrop");

    const contactClose =
        document.getElementById("qtContactClose");

    const contactSearch =
        document.getElementById("qtContactSearch");

    const contactCount =
        document.getElementById("qtContactCount");

    const contactLoading =
        document.getElementById("qtContactLoading");

    const contactEmpty =
        document.getElementById("qtContactEmpty");

    const contactList =
        document.getElementById("qtContactList");


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
    let contactsLoaded = false;


    function openContactModal() {
        if (
            !latestTranslation ||
            !contactModalReady
        ) {
            return;
        }

        contactModal.hidden = false;

        document.body.style.overflow =
            "hidden";

        setTimeout(() => {
            contactSearch.focus();
        }, 100);

        if (!contactsLoaded) {
            loadQuickContacts();
        }
    }


    function closeContactModal() {
        contactModal.hidden = true;

        document.body.style.overflow =
            "";

        contactSearch.value = "";

        renderQuickContacts(
            quickContacts
        );
    }


    function buildContactAvatar(contact) {
        const profilePic = escapeHtml(
            contact.profilePic || ""
        );

        const firstLetter = escapeHtml(
            String(contact.name || "U")
                .charAt(0)
                .toUpperCase()
        );

        if (profilePic) {
            return `
                <div class="qt-contact-avatar">

                    <img src="${profilePic}"
                         alt="${escapeHtml(
                             contact.name || "User"
                         )}"
                         loading="lazy"
                         onerror="
                            this.parentElement.innerHTML=
                            '${firstLetter}'
                         ">

                </div>
            `;
        }

        return `
            <div class="qt-contact-avatar">
                ${firstLetter}
            </div>
        `;
    }


    function renderQuickContacts(contacts) {
        contactList.innerHTML = "";

        if (
            !Array.isArray(contacts) ||
            contacts.length === 0
        ) {
            contactEmpty.hidden = false;

            contactCount.textContent =
                "0 contacts";

            return;
        }

        contactEmpty.hidden = true;

        contactCount.textContent =
            `${contacts.length} contact${
                contacts.length === 1
                    ? ""
                    : "s"
            }`;


        contactList.innerHTML = contacts
            .map((contact) => {
                return `
                    <button type="button"
                            class="qt-contact-item"
                            data-mobile="${escapeHtml(
                                contact.mobile
                            )}">

                        ${buildContactAvatar(contact)}

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
            })
            .join("");


        contactList
            .querySelectorAll(
                ".qt-contact-item"
            )
            .forEach((button) => {

                button.addEventListener(
                    "click",
                    () => {
                        sendTranslationToContact(
                            button
                        );
                    }
                );

            });
    }


    async function loadQuickContacts() {
        contactLoading.hidden = false;
        contactEmpty.hidden = true;
        contactList.innerHTML = "";
        contactCount.textContent = "";

        try {
            const response = await fetch(
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

            if (!response.ok || !data.success) {
                throw new Error(
                    data.error ||
                    "Unable to load contacts"
                );
            }

            quickContacts =
                Array.isArray(data.items)
                    ? data.items
                    : [];

            contactsLoaded = true;

            renderQuickContacts(
                quickContacts
            );

        } catch (error) {
            console.error(
                "QUICK CONTACTS ERROR:",
                error
            );

            contactEmpty.hidden = false;

            contactEmpty.innerHTML = `
                <i class="bi bi-exclamation-circle"></i>

                <strong>
                    Unable to load contacts
                </strong>
            `;

        } finally {
            contactLoading.hidden = true;
        }
    }


    async function sendTranslationToContact(
        button
    ) {
        const receiverMobile =
            String(
                button.dataset.mobile || ""
            ).trim();

        if (
            !receiverMobile ||
            !latestTranslation
        ) {
            return;
        }

        const oldContent =
            button.innerHTML;

        button.disabled = true;

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

            const response = await fetch(
                "/send-message",
                {
                    method: "POST",
                    body: formData
                }
            );

            const data =
                await response.json();

            if (!response.ok || !data.success) {
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

            setTimeout(() => {
                closeContactModal();
            }, 900);

        } catch (error) {
            console.error(
                "QUICK TRANSLATE SEND ERROR:",
                error
            );

            button.disabled = false;
            button.innerHTML = oldContent;

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

                            return searchValue.includes(
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
                event.key === "Escape" &&
                !contactModal.hidden
            ) {
                closeContactModal();
            }
        }
    );


    /* =========================================
       INITIAL STATE
    ========================================= */

    charCount.textContent =
        `${input.value.length} / 5000`;

    sourceLabel.textContent =
        getLanguageName(source);

    showEmptyOutput();

});