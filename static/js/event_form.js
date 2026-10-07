document.addEventListener("DOMContentLoaded", () => {
    const venue = document.getElementById("id_venue");
    const newVenue = document.getElementById("new-venue-fields");
    const ticketed = document.getElementById("id_is_ticketed");
    const fee = document.getElementById("fee-field");

    const syncVenue = () => {
        if (venue && newVenue) newVenue.style.display = venue.value ? "none" : "block";
    };
    const syncFee = () => {
        if (ticketed && fee) fee.style.display = ticketed.checked ? "block" : "none";
    };

    if (venue) venue.addEventListener("change", syncVenue);
    if (ticketed) ticketed.addEventListener("change", syncFee);
    syncVenue();
    syncFee();
});
