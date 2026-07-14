document.addEventListener("DOMContentLoaded", function () {

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


                const reader = new FileReader();

                reader.onload = function (event) {

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


    const passwordForm =
        document.getElementById("passwordForm");


    if (passwordForm) {

        passwordForm.addEventListener(
            "submit",
            function (event) {

                const newPassword =
                    document.getElementById(
                        "newPassword"
                    ).value;

                const confirmPassword =
                    document.getElementById(
                        "confirmPassword"
                    ).value;


                if (newPassword !== confirmPassword) {

                    event.preventDefault();

                    alert(
                        "New passwords do not match."
                    );

                }

            }
        );

    }

});