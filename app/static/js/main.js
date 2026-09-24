/* =========================================================
   MAIN APPLICATION JAVASCRIPT
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        /*
         * General application-level JavaScript
         *
         * Navbar hide/show logic is handled
         * separately inside navbar.js.
         *
         * This file is intentionally kept clean
         * so multiple navbar event listeners do not
         * conflict with each other.
         */


        /* =====================================================
           FLASH MESSAGE AUTO HIDE
           ===================================================== */

        const flashMessages =
            document.querySelectorAll(
                ".flash-message"
            );


        flashMessages.forEach(
            function (message) {

                setTimeout(
                    function () {

                        message.style.opacity = "0";

                        message.style.transform =
                            "translateY(-8px)";

                        setTimeout(
                            function () {

                                message.remove();

                            },
                            300
                        );

                    },
                    4000
                );

            }
        );


        /* =====================================================
           FILE INPUT NAME DISPLAY
           ===================================================== */

        const fileInputs =
            document.querySelectorAll(
                ".file-input"
            );


        fileInputs.forEach(
            function (input) {

                input.addEventListener(
                    "change",
                    function () {

                        if (
                            input.files &&
                            input.files.length > 0
                        ) {

                            const fileName =
                                input.files[0].name;

                            input.setAttribute(
                                "data-selected-file",
                                fileName
                            );

                        }

                    }
                );

            }
        );


        /* =====================================================
           BUTTON LOADING STATE
           ===================================================== */

        const uploadForms =
            document.querySelectorAll(
                'form[enctype="multipart/form-data"]'
            );


        uploadForms.forEach(
            function (form) {

                form.addEventListener(
                    "submit",
                    function () {

                        const submitButton =
                            form.querySelector(
                                'button[type="submit"]'
                            );


                        if (!submitButton) {
                            return;
                        }


                        /*
                         * Do not block the form submission.
                         * Just provide a visual loading state.
                         */

                        submitButton.disabled =
                            true;


                        submitButton.dataset.originalText =
                            submitButton.innerHTML;


                        submitButton.innerHTML =
                            "Processing...";


                    }
                );

            }
        );


        /* =====================================================
           SMOOTH INTERNAL LINKS
           ===================================================== */

        const internalLinks =
            document.querySelectorAll(
                'a[href^="#"]'
            );


        internalLinks.forEach(
            function (link) {

                link.addEventListener(
                    "click",
                    function (event) {

                        const targetId =
                            link.getAttribute(
                                "href"
                            );


                        if (
                            !targetId ||
                            targetId === "#"
                        ) {

                            return;

                        }


                        const target =
                            document.querySelector(
                                targetId
                            );


                        if (!target) {
                            return;
                        }


                        event.preventDefault();


                        target.scrollIntoView(
                            {
                                behavior: "smooth",
                                block: "start"
                            }
                        );

                    }
                );

            }
        );


        /* =====================================================
           CONSOLE INFO
           ===================================================== */

        console.log(
            "AI Document Analyzer loaded successfully."
        );

    }
);