document.addEventListener(
    "DOMContentLoaded",
    function () {

        const tabs =
            document.querySelectorAll(
                ".media-tab"
            );

        const panels =
            document.querySelectorAll(
                ".media-panel"
            );

        const modal =
            document.getElementById(
                "mediaPreviewModal"
            );

        const previewTitle =
            document.getElementById(
                "previewTitle"
            );

        const previewBody =
            document.getElementById(
                "previewBody"
            );

        const previewDownload =
            document.getElementById(
                "previewDownload"
            );


        function activateTab(tabName) {
            tabs.forEach(function (tab) {
                tab.classList.toggle(
                    "active",
                    tab.dataset.tab === tabName
                );
            });

            panels.forEach(function (panel) {
                panel.classList.toggle(
                    "active",
                    panel.dataset.panel === tabName
                );
            });
        }


        tabs.forEach(function (tab) {
            tab.addEventListener(
                "click",
                function () {
                    activateTab(
                        tab.dataset.tab
                    );
                }
            );
        });


        function makeDownloadUrl(
            url,
            name
        ) {
            return (
                "/download-file?url=" +
                encodeURIComponent(url) +
                "&name=" +
                encodeURIComponent(
                    name || "basha-file"
                )
            );
        }


        function openPreview(
            url,
            fileType,
            fileName
        ) {
            if (!url || !modal) {
                return;
            }

            previewTitle.textContent =
                fileName || "File Preview";

            previewBody.innerHTML = "";

            previewDownload.href =
                makeDownloadUrl(
                    url,
                    fileName
                );

            if (fileType === "image") {
                const image =
                    document.createElement(
                        "img"
                    );

                image.src = url;
                image.alt =
                    fileName || "Shared image";

                previewBody.appendChild(
                    image
                );
            } else {
                const frame =
                    document.createElement(
                        "iframe"
                    );

                frame.src = url;
                frame.title =
                    fileName || "Document preview";

                previewBody.appendChild(
                    frame
                );
            }

            modal.hidden = false;

            document.body.classList.add(
                "preview-open"
            );
        }


        function closePreview() {
            if (!modal) {
                return;
            }

            modal.hidden = true;

            previewBody.innerHTML = "";

            document.body.classList.remove(
                "preview-open"
            );
        }


        document
            .querySelectorAll(
                "[data-preview-url]"
            )
            .forEach(function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        openPreview(
                            button.dataset.previewUrl,
                            button.dataset.previewType,
                            button.dataset.previewName
                        );

                    }
                );

            });


        document
            .querySelectorAll(
                "[data-close-preview]"
            )
            .forEach(function (button) {

                button.addEventListener(
                    "click",
                    closePreview
                );

            });


        document.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Escape"
                    && modal
                    && !modal.hidden
                ) {
                    closePreview();
                }

            }
        );

    }
);