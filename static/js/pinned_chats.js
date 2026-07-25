document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById(
        "pinnedChatsContainer"
    );

    if (!container) {
        return;
    }

    function escapeHtml(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function getChatIcon(chatType) {
        if (chatType === "group") {
            return "bi-people-fill";
        }

        return "bi-person-fill";
    }

    function buildAvatar(item) {
        const profilePic = escapeHtml(
            item.profilePic || ""
        );

        if (profilePic) {
            return `
                <img
                    src="${profilePic}"
                    class="pin-avatar-image"
                    alt="${escapeHtml(item.title || "Chat")}"
                    loading="lazy"
                    onerror="
                        this.style.display='none';
                        this.nextElementSibling.style.display='flex';
                    "
                >

                <div
                    class="pin-avatar pin-avatar-fallback"
                    style="display:none;"
                >
                    <i class="bi ${getChatIcon(item.chatType)}"></i>
                </div>
            `;
        }

        return `
            <div class="pin-avatar">
                <i class="bi ${getChatIcon(item.chatType)}"></i>
            </div>
        `;
    }

    function renderEmpty() {
        container.innerHTML = `
            <div class="pinned-empty-state">
                <i class="bi bi-pin-angle"></i>

                <div>
                    <strong>No pinned chats</strong>
                    <p>
                        Pin important personal or group chats
                        to access them quickly.
                    </p>
                </div>
            </div>
        `;
    }

    function renderError() {
        container.innerHTML = `
            <div class="pinned-empty-state pinned-error-state">
                <i class="bi bi-exclamation-circle"></i>

                <div>
                    <strong>Unable to load pinned chats</strong>
                    <p>Please refresh and try again.</p>
                </div>
            </div>
        `;
    }

    function renderPinnedChats(items) {
        if (!Array.isArray(items) || items.length === 0) {
            renderEmpty();
            return;
        }

        container.innerHTML = items.map((item) => {
            const chatUrl = escapeHtml(
                item.chatUrl || "#"
            );

            const title = escapeHtml(
                item.title || "Chat"
            );

            const lastMessage = escapeHtml(
                item.lastMessage || "Open chat"
            );

            const pinnedAtText = escapeHtml(
                item.pinnedAtText || ""
            );

            const chatType = escapeHtml(
                item.chatType || "individual"
            );

            const mobile = escapeHtml(
                item.mobile || ""
            );

            const groupId = escapeHtml(
                item.groupId || ""
            );

            return `
                <div class="pinned-chat">

                    <a
                        href="${chatUrl}"
                        class="pinned-chat-open"
                    >

                        <div class="pin-left">

                            <div class="pin-avatar-wrap">
                                ${buildAvatar(item)}
                            </div>

                            <div class="pin-content">

                                <div class="pin-name">
                                    ${title}
                                </div>

                                <div class="pin-message">
                                    ${lastMessage}
                                </div>

                                ${
                                    pinnedAtText
                                        ? `
                                            <div class="pin-time">
                                                Pinned ${pinnedAtText}
                                            </div>
                                        `
                                        : ""
                                }

                            </div>

                        </div>

                    </a>

                    <button
                        type="button"
                        class="pin-remove-button"
                        data-chat-type="${chatType}"
                        data-mobile="${mobile}"
                        data-group-id="${groupId}"
                        title="Unpin chat"
                        aria-label="Unpin ${title}"
                    >
                        <i class="bi bi-pin-angle-fill"></i>
                    </button>

                </div>
            `;
        }).join("");

        attachUnpinListeners();
    }

    async function loadPinnedChats() {
        container.innerHTML = `
            <div class="loading-state">
                <span
                    class="spinner-border spinner-border-sm"
                    role="status"
                ></span>

                Loading pinned chats...
            </div>
        `;

        try {
            const response = await fetch(
                "/api/pinned-chats?limit=5",
                {
                    headers: {
                        "Accept": "application/json"
                    }
                }
            );

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(
                    data.error || "Unable to load pinned chats"
                );
            }

            renderPinnedChats(data.items);

        } catch (error) {
            console.error(
                "PINNED CHATS LOAD ERROR:",
                error
            );

            renderError();
        }
    }

    async function unpinChat(button) {
        const chatType =
            button.dataset.chatType || "individual";

        const mobile =
            button.dataset.mobile || "";

        const groupId =
            button.dataset.groupId || "";

        button.disabled = true;

        const oldIcon = button.innerHTML;

        button.innerHTML = `
            <span
                class="spinner-border spinner-border-sm"
                role="status"
            ></span>
        `;

        try {
            const response = await fetch(
                "/api/unpin-chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },

                    body: JSON.stringify({
                        chatType,
                        mobile,
                        groupId
                    })
                }
            );

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(
                    data.error || "Unable to unpin chat"
                );
            }

            await loadPinnedChats();

        } catch (error) {
            console.error(
                "UNPIN CHAT ERROR:",
                error
            );

            button.disabled = false;
            button.innerHTML = oldIcon;

            alert(
                error.message ||
                "Unable to unpin chat"
            );
        }
    }

    function attachUnpinListeners() {
        const buttons = container.querySelectorAll(
            ".pin-remove-button"
        );

        buttons.forEach((button) => {
            button.addEventListener(
                "click",
                (event) => {
                    event.preventDefault();
                    event.stopPropagation();

                    unpinChat(button);
                }
            );
        });
    }

    loadPinnedChats();

    window.reloadPinnedChats = loadPinnedChats;
});