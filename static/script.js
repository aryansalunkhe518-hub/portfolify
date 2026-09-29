/* =========================================================
   PORTFOLIFY - MAIN JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       FLASH MESSAGE AUTO HIDE
       ===================================================== */

    const flashes = document.querySelectorAll(".flash");

    flashes.forEach(function (flash) {
        setTimeout(function () {
            flash.style.transition = "opacity 0.4s ease";
            flash.style.opacity = "0";

            setTimeout(function () {
                flash.remove();
            }, 450);
        }, 4500);
    });


    /* =====================================================
       DELETE CONFIRMATION
       ===================================================== */

    const deleteButtons = document.querySelectorAll("[data-confirm-delete]");

    deleteButtons.forEach(function (button) {
        button.addEventListener("click", function (event) {

            const message =
                button.getAttribute("data-confirm-delete") ||
                "Are you sure you want to delete this?";

            if (!confirm(message)) {
                event.preventDefault();
            }
        });
    });


    /* =====================================================
       PASSWORD SHOW / HIDE
       ===================================================== */

    const passwordToggles = document.querySelectorAll(".password-toggle");

    passwordToggles.forEach(function (toggle) {

        toggle.addEventListener("click", function () {

            const targetId = toggle.getAttribute("data-target");
            const input = document.getElementById(targetId);

            if (!input) {
                return;
            }

            if (input.type === "password") {
                input.type = "text";
                toggle.textContent = "Hide";
            } else {
                input.type = "password";
                toggle.textContent = "Show";
            }
        });
    });


    /* =====================================================
       FILE NAME DISPLAY
       ===================================================== */

    const fileInputs = document.querySelectorAll("input[type='file']");

    fileInputs.forEach(function (input) {

        input.addEventListener("change", function () {

            const file = input.files[0];

            if (!file) {
                return;
            }

            const fileNameElement =
                document.querySelector(
                    "[data-file-name='" + input.name + "']"
                );

            if (fileNameElement) {
                fileNameElement.textContent =
                    "Selected: " + file.name;
            }
        });
    });


    /* =====================================================
       PROFILE PHOTO PREVIEW
       ===================================================== */

    const photoInput = document.querySelector("input[name='photo']");
    const photoPreview = document.querySelector("[data-photo-preview]");

    if (photoInput && photoPreview) {

        photoInput.addEventListener("change", function () {

            const file = photoInput.files[0];

            if (!file) {
                return;
            }

            if (!file.type.startsWith("image/")) {
                return;
            }

            const reader = new FileReader();

            reader.onload = function (event) {
                photoPreview.src = event.target.result;
            };

            reader.readAsDataURL(file);
        });
    }


    /* =====================================================
       LIVE PORTFOLIO PREVIEW
       ===================================================== */

    const previewFields = document.querySelectorAll(
        "[data-preview-field]"
    );

    previewFields.forEach(function (field) {

        field.addEventListener("input", function () {

            const targetName =
                field.getAttribute("data-preview-field");

            const target =
                document.querySelector(
                    "[data-preview='" + targetName + "']"
                );

            if (!target) {
                return;
            }

            target.textContent =
                field.value.trim() ||
                target.getAttribute("data-placeholder") ||
                "Your information";
        });
    });


    /* =====================================================
       TEMPLATE SELECTION
       ===================================================== */

    const templateInputs =
        document.querySelectorAll("input[name='template']");

    const templatePreview =
        document.querySelector("[data-template-preview]");

    templateInputs.forEach(function (input) {

        input.addEventListener("change", function () {

            if (!templatePreview) {
                return;
            }

            templatePreview.className =
                "live-preview template-" + input.value;

            templatePreview.setAttribute(
                "data-selected-template",
                input.value
            );
        });
    });


    /* =====================================================
       THEME SELECTION
       ===================================================== */

    const themeInputs =
        document.querySelectorAll("input[name='theme']");

    const themePreview =
        document.querySelector("[data-theme-preview]");

    themeInputs.forEach(function (input) {

        input.addEventListener("change", function () {

            if (!themePreview) {
                return;
            }

            themePreview.classList.remove(
                "theme-blue",
                "theme-purple",
                "theme-green",
                "theme-orange",
                "theme-red",
                "theme-dark"
            );

            themePreview.classList.add(
                "theme-" + input.value
            );
        });
    });


    /* =====================================================
       FONT SELECTION
       ===================================================== */

    const fontInput =
        document.querySelector("select[name='font']");

    const fontPreview =
        document.querySelector("[data-font-preview]");

    if (fontInput && fontPreview) {

        fontInput.addEventListener("change", function () {

            fontPreview.classList.remove(
                "font-modern",
                "font-classic",
                "font-clean",
                "font-typewriter"
            );

            fontPreview.classList.add(
                "font-" + fontInput.value
            );
        });
    }


    /* =====================================================
       PHOTO STYLE
       ===================================================== */

    const photoStyleInputs =
        document.querySelectorAll("input[name='photo_style']");

    const photoStylePreview =
        document.querySelector("[data-photo-style-preview]");

    photoStyleInputs.forEach(function (input) {

        input.addEventListener("change", function () {

            if (!photoStylePreview) {
                return;
            }

            photoStylePreview.classList.remove(
                "photo-circle",
                "photo-rounded",
                "photo-square"
            );

            photoStylePreview.classList.add(
                "photo-" + input.value
            );
        });
    });


    /* =====================================================
       DECORATION
       ===================================================== */

    const decorationInputs =
        document.querySelectorAll("input[name='decoration']");

    const decorationPreview =
        document.querySelector("[data-decoration-preview]");

    decorationInputs.forEach(function (input) {

        input.addEventListener("change", function () {

            if (!decorationPreview) {
                return;
            }

            decorationPreview.classList.remove(
                "decoration-sparkle",
                "decoration-developer",
                "decoration-creative",
                "decoration-professional",
                "decoration-tech"
            );

            decorationPreview.classList.add(
                "decoration-" + input.value
            );
        });
    });


    /* =====================================================
       RESUME VALIDATION
       ===================================================== */

    const resumeInput =
        document.querySelector("input[name='resume']");

    if (resumeInput) {

        resumeInput.addEventListener("change", function () {

            const file = resumeInput.files[0];

            if (!file) {
                return;
            }

            const allowedTypes = [
                "application/pdf",
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ];

            const maxSize = 8 * 1024 * 1024;

            if (!allowedTypes.includes(file.type)) {

                alert(
                    "Please upload a PDF, DOC, or DOCX resume."
                );

                resumeInput.value = "";
                return;
            }

            if (file.size > maxSize) {

                alert(
                    "Resume size must be less than 8 MB."
                );

                resumeInput.value = "";
            }
        });
    }


    /* =====================================================
       COPY PUBLIC PORTFOLIO LINK
       ===================================================== */

    const copyButtons =
        document.querySelectorAll("[data-copy-link]");

    copyButtons.forEach(function (button) {

        button.addEventListener("click", async function () {

            const link =
                button.getAttribute("data-copy-link");

            if (!link) {
                return;
            }

            try {

                await navigator.clipboard.writeText(link);

                const oldText = button.textContent;

                button.textContent = "Copied!";

                setTimeout(function () {
                    button.textContent = oldText;
                }, 1800);

            } catch (error) {

                const temporaryInput =
                    document.createElement("input");

                temporaryInput.value = link;

                document.body.appendChild(temporaryInput);

                temporaryInput.select();

                document.execCommand("copy");

                temporaryInput.remove();

                const oldText = button.textContent;

                button.textContent = "Copied!";

                setTimeout(function () {
                    button.textContent = oldText;
                }, 1800);
            }
        });
    });


    /* =====================================================
       PREVENT DOUBLE FORM SUBMISSION
       ===================================================== */

    const forms = document.querySelectorAll("form");

    forms.forEach(function (form) {

        form.addEventListener("submit", function () {

            const submitButton =
                form.querySelector(
                    "button[type='submit'], input[type='submit']"
                );

            if (!submitButton) {
                return;
            }

            setTimeout(function () {

                submitButton.disabled = true;

                if (submitButton.tagName === "BUTTON") {
                    submitButton.dataset.originalText =
                        submitButton.textContent;

                    submitButton.textContent =
                        "Please wait...";
                }

            }, 20);
        });
    });


    /* =====================================================
       CHARACTER COUNTERS
       ===================================================== */

    const counterFields =
        document.querySelectorAll("[data-max-length]");

    counterFields.forEach(function (field) {

        const max =
            Number(field.getAttribute("data-max-length"));

        if (!max) {
            return;
        }

        const counter =
            document.querySelector(
                "[data-counter='" + field.name + "']"
            );

        function updateCounter() {

            if (!counter) {
                return;
            }

            counter.textContent =
                field.value.length + " / " + max;
        }

        field.addEventListener("input", updateCounter);

        updateCounter();
    });


    /* =====================================================
       SMOOTH SCROLL
       ===================================================== */

    const scrollLinks =
        document.querySelectorAll("a[href^='#']");

    scrollLinks.forEach(function (link) {

        link.addEventListener("click", function (event) {

            const targetId =
                link.getAttribute("href");

            if (!targetId || targetId === "#") {
                return;
            }

            const target =
                document.querySelector(targetId);

            if (!target) {
                return;
            }

            event.preventDefault();

            target.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        });
    });


    /* =====================================================
       PAGE FADE IN
       ===================================================== */

    document.body.classList.add("page-ready");

});