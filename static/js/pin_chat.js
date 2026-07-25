document.addEventListener("DOMContentLoaded", () => {
    const pinButton = document.getElementById("pinChatBtn");
    const receiverInput = document.getElementById("receiver_mobile");

    if (!pinButton || !receiverInput) {
        return;
    }

    const receiverMobile = String(receiverInput.value || "").trim();

    if (!receiverMobile) {
        pinButton.style.display = "none";
        return;
    }

    let isPinned = false;
    let isWorking = false;

    function updateButton() {
        pinButton.classList.toggle("is-pinned", isPinned);

        pinButton.title = isPinned
            ? "Unpin Chat"
            : "Pin Chat";

        pinButton.setAttribute(
            "aria-label",
            isPinned ? "Unpin Chat" : "Pin Chat"
        );

        pinButton.innerHTML = isPinned
            ? "📍"
            : "📌";
    }

    function setLoading(loading) {
        isWorking = loading;
        pinButton.disabled = loading;

        if (loading) {
            pinButton.innerHTML = `
                <span class="spinner-border spinner-border-sm"></span>
            `;
        } else {
            updateButton();
        }
    }

    async function checkPinnedStatus() {
        try {
            const response = await fetch(
                "/api/pinned-chats?limit=20",
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
                    data.error || "Unable to check pin status"
                );
            }

            const items = Array.isArray(data.items)
                ? data.items
                : [];

            isPinned = items.some((item) => {
                return (
                    item.chatType === "individual" &&
                    String(item.mobile || "").trim() === receiverMobile
                );
            });

            updateButton();

        } catch (error) {
            console.error("PIN STATUS ERROR:", error);
            updateButton();
        }
    }

    async function pinChat() {
        const response = await fetch(
            "/api/pin-chat",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },

                body: JSON.stringify({
                    chatType: "individual",
                    mobile: receiverMobile
                })
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.error || "Unable to pin chat"
            );
        }

        isPinned = true;
    }

    async function unpinChat() {
        const response = await fetch(
            "/api/unpin-chat",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },

                body: JSON.stringify({
                    chatType: "individual",
                    mobile: receiverMobile,
                    groupId: ""
                })
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.error || "Unable to unpin chat"
            );
        }

        isPinned = false;
    }

    pinButton.addEventListener("click", async () => {
        if (isWorking) {
            return;
        }

        setLoading(true);

        try {
            if (isPinned) {
                await unpinChat();
            } else {
                await pinChat();
            }

            updateButton();

        } catch (error) {
            console.error("PIN CHAT ERROR:", error);

            alert(
                error.message ||
                "Unable to update pinned chat"
            );

        } finally {
            setLoading(false);
        }
    });

    checkPinnedStatus();
});