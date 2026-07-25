document.addEventListener("DOMContentLoaded", () => {
    const card = document.getElementById("quickTranslateCard");

    if (!card) return;

    const toggle = document.getElementById("qtToggle");
    const collapse = document.getElementById("qtCollapse");

    const source = document.getElementById("qtSourceLanguage");
    const target = document.getElementById("qtTargetLanguage");
    const swap = document.getElementById("qtSwapBtn");

    const input = document.getElementById("qtInput");
    const charCount = document.getElementById("qtCharCount");
    const clearBtn = document.getElementById("qtClearBtn");
    const translateBtn = document.getElementById("qtTranslateBtn");

    const errorBox = document.getElementById("qtError");
    const result = document.getElementById("qtResult");
    const translatedText = document.getElementById("qtTranslatedText");
    const resultLanguage = document.getElementById("qtResultLanguage");

    const copyBtn = document.getElementById("qtCopyBtn");
    const copyActionBtn = document.getElementById("qtCopyActionBtn");
    const sendBtn = document.getElementById("qtSendBtn");

    let latestTranslation = "";

    function escapeHtml(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function openCard() {
        collapse.hidden = false;
        toggle.setAttribute("aria-expanded", "true");
    }

    function closeCard() {
        collapse.hidden = true;
        toggle.setAttribute("aria-expanded", "false");
    }

    toggle.addEventListener("click", () => {
        collapse.hidden ? openCard() : closeCard();
    });

    input.addEventListener("input", () => {
        charCount.textContent = `${input.value.length} / 5000`;
    });

    clearBtn.addEventListener("click", () => {
        input.value = "";
        charCount.textContent = "0 / 5000";
        errorBox.hidden = true;
        result.hidden = true;
        latestTranslation = "";
        input.focus();
    });

    swap.addEventListener("click", () => {
        if (source.value === "auto") {
            return;
        }

        const oldSource = source.value;
        source.value = target.value;
        target.value = oldSource;
    });

    async function translateText() {
        const text = input.value.trim();

        errorBox.hidden = true;
        result.hidden = true;

        if (!text) {
            errorBox.textContent = "Please enter text.";
            errorBox.hidden = false;
            input.focus();
            return;
        }

        translateBtn.disabled = true;
        translateBtn.innerHTML = `
            <span class="spinner-border spinner-border-sm"></span>
            Translating...
        `;

        try {
            const response = await fetch("/api/quick-translate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify({
                    text,
                    sourceLanguage: source.value,
                    targetLanguage: target.value
                })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.error || "Translation failed");
            }

            latestTranslation = data.translated || "";

            translatedText.textContent = latestTranslation;
            resultLanguage.textContent =
                `${data.sourceLanguageName} → ${data.targetLanguageName}`;

            result.hidden = false;

        } catch (error) {
            console.error("QUICK TRANSLATE ERROR:", error);

            errorBox.textContent =
                error.message || "Unable to translate.";
            errorBox.hidden = false;

        } finally {
            translateBtn.disabled = false;
            translateBtn.innerHTML = `
                <i class="bi bi-translate"></i>
                Translate
            `;
        }
    }

    async function copyTranslation() {
        if (!latestTranslation) return;

        try {
            await navigator.clipboard.writeText(latestTranslation);

            copyActionBtn.innerHTML = `
                <i class="bi bi-check-lg"></i>
                Copied
            `;

            setTimeout(() => {
                copyActionBtn.innerHTML = `
                    <i class="bi bi-copy"></i>
                    Copy
                `;
            }, 1200);

        } catch (error) {
            alert("Unable to copy text.");
        }
    }

    translateBtn.addEventListener("click", translateText);
    copyBtn.addEventListener("click", copyTranslation);
    copyActionBtn.addEventListener("click", copyTranslation);

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
        if (!latestTranslation || !contactModalReady) {
            return;
        }

        contactModal.hidden = false;
        document.body.style.overflow = "hidden";

        setTimeout(() => {
            contactSearch.focus();
        }, 100);

        if (!contactsLoaded) {
            loadQuickContacts();
        }
    }

    function closeContactModal() {
        contactModal.hidden = true;
        document.body.style.overflow = "";
        contactSearch.value = "";
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
                        alt="${escapeHtml(contact.name || "User")}"
                        loading="lazy"
                        onerror="
                            this.parentElement.innerHTML='${firstLetter}'
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

        if (!Array.isArray(contacts) || contacts.length === 0) {
            contactEmpty.hidden = false;
            contactCount.textContent = "0 contacts";
            return;
        }

        contactEmpty.hidden = true;

        contactCount.textContent =
            `${contacts.length} contact${contacts.length === 1 ? "" : "s"}`;

        contactList.innerHTML = contacts
            .map((contact) => {
                return `
                    <button type="button"
                            class="qt-contact-item"
                            data-mobile="${escapeHtml(contact.mobile)}">

                        ${buildContactAvatar(contact)}

                        <div class="qt-contact-info">

                            <div class="qt-contact-name">
                                ${escapeHtml(contact.name || "User")}
                            </div>

                            <div class="qt-contact-meta">
                                ${escapeHtml(contact.mobile || "")}
                                ${
                                    contact.languageName
                                        ? ` • ${escapeHtml(contact.languageName)}`
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
            .querySelectorAll(".qt-contact-item")
            .forEach((button) => {
                button.addEventListener("click", () => {
                    sendTranslationToContact(button);
                });
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
                        "Accept": "application/json"
                    },
                    cache: "no-store"
                }
            );

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(
                    data.error || "Unable to load contacts"
                );
            }

            quickContacts = Array.isArray(data.items)
                ? data.items
                : [];

            contactsLoaded = true;

            renderQuickContacts(quickContacts);

        } catch (error) {
            console.error(
                "QUICK CONTACTS ERROR:",
                error
            );

            contactEmpty.hidden = false;
            contactEmpty.innerHTML = `
                <i class="bi bi-exclamation-circle"></i>
                <strong>Unable to load contacts</strong>
            `;

        } finally {
            contactLoading.hidden = true;
        }
    }

    async function sendTranslationToContact(button) {
        const receiverMobile =
            String(button.dataset.mobile || "").trim();

        if (!receiverMobile || !latestTranslation) {
            return;
        }

        const oldContent = button.innerHTML;

        button.disabled = true;

        const icon = button.querySelector(
            ".qt-contact-send-icon"
        );

        if (icon) {
            icon.innerHTML = `
                <span class="spinner-border spinner-border-sm"></span>
            `;
        }

        try {
            const formData = new FormData();

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

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(
                    data.error || "Unable to send message"
                );
            }

            button.classList.add("is-sent");

            if (icon) {
                icon.innerHTML =
                    '<i class="bi bi-check-lg"></i>';
            }

            const name = button.querySelector(
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

        contactSearch.addEventListener("input", () => {
            const query =
                contactSearch.value.trim().toLowerCase();

            const filteredContacts = quickContacts.filter(
                (contact) => {
                    const searchValue = `
                        ${contact.name || ""}
                        ${contact.mobile || ""}
                        ${contact.languageName || ""}
                    `.toLowerCase();

                    return searchValue.includes(query);
                }
            );

            renderQuickContacts(filteredContacts);
        });

        contactClose.addEventListener(
            "click",
            closeContactModal
        );

        contactBackdrop.addEventListener(
            "click",
            closeContactModal
        );
    }

    document.addEventListener("keydown", (event) => {
        if (
            contactModalReady &&
            event.key === "Escape" &&
            !contactModal.hidden
        ) {
            closeContactModal();
        }
    });
});