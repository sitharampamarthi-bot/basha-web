document.addEventListener("DOMContentLoaded", () => {
    const card = document.getElementById("homeRecentFilesCard");

    if (!card) return;

    const toggle = document.getElementById("recentFilesToggle");
    const collapse = document.getElementById("recentFilesCollapse");
    const headerTotal = document.getElementById("recentHeaderTotal");

    const loading = document.getElementById("recentFilesLoading");
    const empty = document.getElementById("recentFilesEmpty");
    const list = document.getElementById("recentFilesList");
    const footerLink = document.getElementById("recentFilesFooterLink");

    const countAll = document.getElementById("recentCountAll");
    const countImages = document.getElementById("recentCountImages");
    const countVideos = document.getElementById("recentCountVideos");
    const countAudio = document.getElementById("recentCountAudio");
    const countDocuments = document.getElementById("recentCountDocuments");

    const filterButtons = Array.from(
        card.querySelectorAll("[data-recent-filter]")
    );

    let activeType = "all";
    let isLoaded = false;
    let activeController = null;

    function escapeHtml(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function typeLabel(type) {
        return {
            image: "Photo",
            video: "Video",
            audio: "Audio",
            document: "Document"
        }[type] || "File";
    }

    function typeIcon(type) {
        return {
            image: "bi-image-fill",
            video: "bi-camera-video-fill",
            audio: "bi-mic-fill",
            document: "bi-file-earmark-text-fill"
        }[type] || "bi-file-earmark-fill";
    }

    function renderPreview(item) {
        const fileUrl = escapeHtml(item.fileUrl || "");
        const fileType = item.type || "document";

        if (fileType === "image") {
            return `
                <div class="recent-file-preview">
                    <img src="${fileUrl}"
                         alt="${escapeHtml(item.title || "Photo")}"
                         loading="lazy"
                         onerror="this.parentElement.innerHTML='<i class=&quot;bi bi-image-fill&quot;></i>'">
                </div>
            `;
        }

        if (fileType === "video") {
            return `
                <div class="recent-file-preview">
                    <video src="${fileUrl}"
                           preload="metadata"
                           muted></video>
                </div>
            `;
        }

        return `
            <div class="recent-file-preview">
                <i class="bi ${typeIcon(fileType)}"></i>
            </div>
        `;
    }

    function updateCounts(counts = {}) {
        countAll.textContent = counts.all || 0;
        countImages.textContent = counts.images || 0;
        countVideos.textContent = counts.videos || 0;
        countAudio.textContent = counts.audio || 0;
        countDocuments.textContent = counts.documents || 0;
        headerTotal.textContent = counts.all || 0;
    }

    function renderItems(items) {
        list.innerHTML = "";

        if (!Array.isArray(items) || items.length === 0) {
            empty.hidden = false;
            return;
        }

        empty.hidden = true;

        list.innerHTML = items.map((item) => {
            const fileType = item.type || "document";

            return `
                <a href="${escapeHtml(item.chatUrl || "#")}"
                   class="recent-file-item">

                    ${renderPreview(item)}

                    <div class="recent-file-body">
                        <div class="recent-file-name">
                            ${escapeHtml(item.title || "Shared file")}
                        </div>

                        <div class="recent-file-meta">
                            ${escapeHtml(item.chatName || "Chat")}
                            ${
                                item.timestampText
                                    ? ` • ${escapeHtml(item.timestampText)}`
                                    : ""
                            }
                        </div>

                        <span class="recent-file-type">
                            <i class="bi ${typeIcon(fileType)}"></i>
                            ${typeLabel(fileType)}
                        </span>
                    </div>

                    <i class="bi bi-chevron-right recent-file-arrow"></i>
                </a>
            `;
        }).join("");
    }

    function setActiveButton(type) {
        filterButtons.forEach((button) => {
            button.classList.toggle(
                "active",
                button.dataset.recentFilter === type
            );
        });
    }

    async function loadRecentFiles(type = "all") {
        activeType = type;

        if (activeController) {
            activeController.abort();
        }

        activeController = new AbortController();

        setActiveButton(type);
        loading.hidden = false;
        empty.hidden = true;
        list.innerHTML = "";

        footerLink.href =
            type === "all"
                ? "/recent-files"
                : `/recent-files?type=${encodeURIComponent(type)}`;

        try {
            const response = await fetch(
                `/api/recent-files?type=${encodeURIComponent(type)}&limit=10`,
                {
                    signal: activeController.signal,
                    headers: {
                        "Accept": "application/json"
                    }
                }
            );

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.error || "Unable to load recent files");
            }

            updateCounts(data.counts);
            renderItems(data.items);
            isLoaded = true;

        } catch (error) {
            if (error.name === "AbortError") return;

            console.error("RECENT FILES ERROR:", error);

            empty.hidden = false;
            empty.innerHTML = `
                <i class="bi bi-exclamation-circle"></i>
                <h5>Unable to load recent files</h5>
                <p>Please refresh and try again.</p>
            `;
        } finally {
            loading.hidden = true;
        }
    }

    function openRecentFiles() {
        collapse.hidden = false;
        toggle.setAttribute("aria-expanded", "true");

        if (!isLoaded) {
            loadRecentFiles(activeType);
        }
    }

    function closeRecentFiles() {
        collapse.hidden = true;
        toggle.setAttribute("aria-expanded", "false");
    }

    toggle.addEventListener("click", () => {
        if (collapse.hidden) {
            openRecentFiles();
        } else {
            closeRecentFiles();
        }
    });

    filterButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const type = button.dataset.recentFilter || "all";

            if (collapse.hidden) {
                openRecentFiles();
            }

            loadRecentFiles(type);
        });
    });

    // Counts matrame initial ga load chestundi.
    fetch("/api/recent-files?type=all&limit=1", {
        headers: {
            "Accept": "application/json"
        }
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                updateCounts(data.counts);
            }
        })
        .catch((error) => {
            console.error("RECENT COUNTS ERROR:", error);
        });
});