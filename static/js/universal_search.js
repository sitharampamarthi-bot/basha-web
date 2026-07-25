document.addEventListener("DOMContentLoaded", () => {

    const input = document.querySelector('input[name="q"]');

    if (!input) return;

    let timer = null;

    input.focus();

    input.addEventListener("input", function () {

        clearTimeout(timer);

        timer = setTimeout(() => {

            const value = input.value.trim();

            if (value.length >= 2) {

                window.location.href =
                    "/search?q=" +
                    encodeURIComponent(value);

            }

        }, 500);

    });

});