document.addEventListener("DOMContentLoaded", function () {

    /* =========================================
       PROFILE IMAGE PREVIEW
    ========================================= */

    const profileInput =
        document.getElementById("profileImageInput");

    const profilePreview =
        document.getElementById("profileImagePreview");

    if (profileInput && profilePreview) {

        profileInput.addEventListener(
            "change",
            function () {

                const file =
                    profileInput.files &&
                    profileInput.files[0];

                if (!file) {
                    return;
                }

                if (!file.type.startsWith("image/")) {

                    alert(
                        "Please select an image file."
                    );

                    profileInput.value = "";
                    return;
                }

                if (file.size > 5 * 1024 * 1024) {

                    alert(
                        "Profile image must be below 5 MB."
                    );

                    profileInput.value = "";
                    return;
                }

                const reader =
                    new FileReader();

                reader.onload =
                    function (event) {

                        profilePreview.innerHTML = `
                            <img
                                src="${event.target.result}"
                                alt="Profile preview">
                        `;
                    };

                reader.readAsDataURL(file);
            }
        );
    }


    /* =========================================
       PASSWORD VALIDATION
    ========================================= */

    const passwordForm =
        document.getElementById("passwordForm");

    if (passwordForm) {

        passwordForm.addEventListener(
            "submit",
            function (event) {

                const newPasswordElement =
                    document.getElementById(
                        "newPassword"
                    );

                const confirmPasswordElement =
                    document.getElementById(
                        "confirmPassword"
                    );

                if (
                    !newPasswordElement ||
                    !confirmPasswordElement
                ) {
                    return;
                }

                if (
                    newPasswordElement.value !==
                    confirmPasswordElement.value
                ) {
                    event.preventDefault();

                    alert(
                        "New passwords do not match."
                    );
                }
            }
        );
    }


    /* =========================================
       SETTINGS SEARCH
    ========================================= */

    const searchToggle =
        document.getElementById(
            "settingsSearchToggle"
        );

    const searchToggleIcon =
        document.getElementById(
            "settingsSearchToggleIcon"
        );

    const searchPanel =
        document.getElementById(
            "settingsSearchPanel"
        );

    const searchInput =
        document.getElementById(
            "settingsSearchInput"
        );

    const searchClear =
        document.getElementById(
            "settingsSearchClear"
        );

    const searchHelp =
        document.getElementById(
            "settingsSearchHelp"
        );

    const searchEmpty =
        document.getElementById(
            "settingsSearchEmpty"
        );

    const searchItems =
        Array.from(
            document.querySelectorAll(
                ".settings-search-item"
            )
        );


    function normalizeSearchText(value) {

        return String(value || "")
            .toLocaleLowerCase()
            .normalize("NFD")
            .replace(
                /[\u0300-\u036f]/g,
                ""
            )
            .trim();
    }


    function getSearchableText(item) {

        return normalizeSearchText(
            [
                item.dataset.settingsSearch || "",
                item.textContent || ""
            ].join(" ")
        );
    }


    function resetSearchResults() {

        searchItems.forEach(
            function (item) {

                item.hidden = false;

                item.classList.remove(
                    "settings-search-match"
                );
            }
        );

        if (searchEmpty) {
            searchEmpty.hidden = true;
        }

        if (searchHelp) {
            searchHelp.textContent =
                "Search profile, mobile, email, language or password";
        }
    }


    function filterSettings() {

        if (!searchInput) {
            return;
        }

        const query =
            normalizeSearchText(
                searchInput.value
            );

        if (searchClear) {
            searchClear.hidden =
                query.length === 0;
        }

        if (!query) {
            resetSearchResults();
            return;
        }

        let matchCount = 0;

        searchItems.forEach(
            function (item) {

                const searchableText =
                    getSearchableText(item);

                const matched =
                    searchableText.includes(query);

                item.hidden =
                    !matched;

                item.classList.toggle(
                    "settings-search-match",
                    matched
                );

                if (matched) {
                    matchCount++;
                }
            }
        );

        if (searchEmpty) {
            searchEmpty.hidden =
                matchCount !== 0;
        }

        if (searchHelp) {

            if (matchCount === 0) {
                searchHelp.textContent =
                    `No results for "${searchInput.value.trim()}"`;
            } else {
                searchHelp.textContent =
                    `${matchCount} setting${matchCount === 1 ? "" : "s"} found`;
            }
        }
    }


    function openSettingsSearch() {

        if (!searchPanel) {
            return;
        }

        searchPanel.hidden = false;

        if (searchToggleIcon) {
            searchToggleIcon.className =
                "bi bi-x-lg";
        }

        window.setTimeout(
            function () {
                searchInput?.focus();
            },
            100
        );
    }


    function closeSettingsSearch() {

        if (!searchPanel) {
            return;
        }

        searchPanel.hidden = true;

        if (searchInput) {
            searchInput.value = "";
        }

        if (searchClear) {
            searchClear.hidden = true;
        }

        if (searchToggleIcon) {
            searchToggleIcon.className =
                "bi bi-search";
        }

        resetSearchResults();
    }


    if (
        searchToggle &&
        searchPanel
    ) {

        searchToggle.addEventListener(
            "click",
            function () {

                if (searchPanel.hidden) {
                    openSettingsSearch();
                } else {
                    closeSettingsSearch();
                }
            }
        );
    }


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            filterSettings
        );

        searchInput.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Escape") {
                    closeSettingsSearch();
                }
            }
        );
    }


    if (searchClear) {

        searchClear.addEventListener(
            "click",
            function () {

                searchInput.value = "";

                resetSearchResults();

                searchClear.hidden = true;

                searchInput.focus();
            }
        );
    }

});