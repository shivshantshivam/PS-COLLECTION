document.addEventListener("DOMContentLoaded", function () {

    const hours = document.getElementById("deal-hours");
    const minutes = document.getElementById("deal-minutes");
    const seconds = document.getElementById("deal-seconds");

    if (!hours || !minutes || !seconds) {
        return;
    }


    /*
       12 hours 45 minutes 30 seconds
    */

    let totalSeconds =
        (12 * 60 * 60) +
        (45 * 60) +
        30;


    function updateTimer() {

        if (totalSeconds <= 0) {

            totalSeconds =
                24 * 60 * 60;

        }


        const h =
            Math.floor(totalSeconds / 3600);


        const m =
            Math.floor(
                (totalSeconds % 3600) / 60
            );


        const s =
            totalSeconds % 60;


        hours.textContent =
            String(h).padStart(2, "0");


        minutes.textContent =
            String(m).padStart(2, "0");


        seconds.textContent =
            String(s).padStart(2, "0");


        totalSeconds--;

    }


    updateTimer();

    setInterval(updateTimer, 1000);

});