/* =========================================================
   NAVBAR AUTO HIDE / SHOW
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const header =
            document.getElementById(
                "siteHeader"
            );


        if (!header) {
            return;
        }


        let lastScrollY =
            window.scrollY;


        let ticking =
            false;


        const showNavbar =
            function () {

                header.classList.remove(
                    "navbar-hidden"
                );

                header.classList.add(
                    "navbar-visible"
                );

            };


        const hideNavbar =
            function () {

                header.classList.remove(
                    "navbar-visible"
                );

                header.classList.add(
                    "navbar-hidden"
                );

            };


        function handleScroll() {

            const currentScrollY =
                window.scrollY;


            /*
             * Always visible at top.
             */

            if (
                currentScrollY <= 8
            ) {

                showNavbar();

                lastScrollY =
                    currentScrollY;

                ticking =
                    false;

                return;

            }


            /*
             * Scroll down.
             */

            if (
                currentScrollY >
                lastScrollY + 3
            ) {

                hideNavbar();

            }


            /*
             * Scroll up.
             */

            else if (
                currentScrollY <
                lastScrollY - 3
            ) {

                showNavbar();

            }


            lastScrollY =
                currentScrollY;

            ticking =
                false;

        }


        window.addEventListener(
            "scroll",
            function () {

                if (!ticking) {

                    window.requestAnimationFrame(
                        handleScroll
                    );

                    ticking =
                        true;

                }

            },
            {
                passive: true
            }
        );


        /*
         * Initial state.
         */

        showNavbar();

    }
);