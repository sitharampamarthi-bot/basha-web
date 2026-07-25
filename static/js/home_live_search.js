document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("homeSearchForm");
    const input = document.getElementById("homeSearchInput");
    const clearButton = document.getElementById("homeSearchClear");
    const dropdown = document.getElementById("homeSearchDropdown");
    const loading = document.getElementById("homeSearchLoading");
    const resultsContainer = document.getElementById("homeSearchResults");
    const viewAll = document.getElementById("homeSearchViewAll");

    if (
        !form ||
        !input ||
        !clearButton ||
        !dropdown ||
        !loading ||
        !resultsContainer ||
        !viewAll
    ) {
        return;
    }

    let searchTimer = null;
    let activeController = null;

    const MAX_RESULTS = 10;

    const categoryOrder = [
        "contacts",
        "groups",
        "messages",
        "images",
        "videos",
        "audio",
        "documents"
    ];

    const typeIcons = {
        contact: "bi-person-fill",
        group: "bi-people-fill",
        message: "bi-chat-left-text-fill",
        image: "bi-image-fill",
        video: "bi-camera-video-fill",
        audio: "bi-mic-fill",
        document: "bi-file-earmark-text-fill"
    };

    const typeLabels = {
        contact: "Contact",
        group: "Group",
        message: "Message",
        image: "Photo",
        video: "Video",
        audio: "Audio",
        document: "Document"
    };

    function escapeHtml(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function flattenResults(results) {
        const items = [];

        for (const category of categoryOrder) {
            const categoryItems = Array.isArray(results?.[category])
                ? results[category]
                : [];

            for (const item of categoryItems) {
                items.push(item);

                if (items.length >= MAX_RESULTS) {
                    return items;
                }
            }
        }

        return items;
    }

    function showDropdown() {
        dropdown.hidden = false;
    }

    function hideDropdown() {
        dropdown.hidden = true;
    }

    function setLoading(isLoading) {
        loading.hidden = !isLoading;
    }

    function renderEmpty(message) {
        resultsContainer.innerHTML = `
            <div class="live-search-empty">
                <i class="bi bi-search"></i>
                <div>${escapeHtml(message)}</div>
            </div>
        `;
    }

    function renderResults(items) {
        if (!items.length) {
            renderEmpty("No matching chats or files found");
            return;
        }

        resultsContainer.innerHTML = items.map((item) => {
            const type = item.type || "message";
            const icon = typeIcons[type] || typeIcons.message;
            const label = typeLabels[type] || "Message";
            const title = escapeHtml(item.title || "Result");
            const subtitle = escapeHtml(item.subtitle || "");
            const preview = escapeHtml(item.messageText || "");
            const chatUrl = escapeHtml(item.chatUrl || "#");

            return `
                <a href="${chatUrl}" class="live-search-item">
                    <div class="live-search-icon">
                        <i class="bi ${icon}"></i>
                    </div>

                    <div class="live-search-content">
                        <div class="live-search-title">${title}</div>

                        ${
                            subtitle
                                ? `<div class="live-search-subtitle">${subtitle}</div>`
                                : ""
                        }

                        ${
                            preview
                                ? `<div class="live-search-preview">${preview}</div>`
                                : ""
                        }
                    </div>

                    <span class="live-search-type">${label}</span>

                    <i class="bi bi-chevron-right text-muted"></i>
                </a>
            `;
        }).join("");
    }

    async function runSearch(query) {
        if (activeController) {
            activeController.abort();
        }

        activeController = new AbortController();

        showDropdown();
        setLoading(true);
        resultsContainer.innerHTML = "";
        viewAll.hidden = true;

        try {
            const response = await fetch(
                `/api/search?q=${encodeURIComponent(query)}`,
                {
                    signal: activeController.signal,
                    headers: {
                        "Accept": "application/json"
                    }
                }
            );

            const data = await response.json();

            console.log(data);

            if (!response.ok || !data.success) {
                throw new Error(data.error || "Search failed");
            }

            const items = flattenResults(data.results);

            renderResults(items);

            viewAll.href = `/search?q=${encodeURIComponent(query)}`;
            viewAll.hidden = data.total <= 0;
        } catch (error) {
            if (error.name === "AbortError") {
                return;
            }

            console.error("LIVE SEARCH ERROR:", error);
            renderEmpty("Unable to search. Please try again.");
        } finally {
            setLoading(false);
        }
    }

    input.addEventListener("input", () => {
        window.clearTimeout(searchTimer);

        const query = input.value.trim();

        clearButton.hidden = query.length === 0;

        if (query.length < 2) {
            if (activeController) {
                activeController.abort();
            }

            resultsContainer.innerHTML = "";
            viewAll.hidden = true;
            hideDropdown();
            return;
        }

        searchTimer = window.setTimeout(() => {
            runSearch(query);
        }, 450);
    });

    clearButton.addEventListener("click", () => {
        input.value = "";
        clearButton.hidden = true;
        resultsContainer.innerHTML = "";
        viewAll.hidden = true;

        if (activeController) {
            activeController.abort();
        }

        hideDropdown();
        input.focus();
    });

    input.addEventListener("focus", () => {
        if (input.value.trim().length >= 2) {
            showDropdown();
        }
    });

    document.addEventListener("click", (event) => {
        if (!event.target.closest(".home-search-wrapper")) {
            hideDropdown();
        }
    });

    form.addEventListener("submit", (event) => {
        const query = input.value.trim();

        if (query.length < 2) {
            event.preventDefault();
            input.focus();
        }
    });
});