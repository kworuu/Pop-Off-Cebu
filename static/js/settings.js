document.addEventListener("DOMContentLoaded", () => {
    // 1. Tab Navigation
    const tabButtons = document.querySelectorAll(".settings-tab-btn");
    const tabPanes = document.querySelectorAll(".settings-tab-pane");

    tabButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
            const targetId = btn.getAttribute("data-tab");

            tabButtons.forEach((b) => {
                b.style.backgroundColor = "var(--paper-card)";
                b.style.color = "var(--text-ink)";
            });
            tabPanes.forEach((p) => p.style.display = "none");

            btn.style.backgroundColor = "var(--mustard-pop)";
            const activePane = document.getElementById(targetId);
            if (activePane) activePane.style.display = "block";
        });
    });

    // 2. Interactive Live Preview
    const stageInput = document.getElementById("id_business_or_stage_name");
    const bioInput = document.getElementById("id_bio");
    const districtSelect = document.getElementById("id_district");

    const previewStage = document.getElementById("preview-stage");
    const previewBio = document.getElementById("preview-bio");
    const previewDistrict = document.getElementById("preview-district");

    if (stageInput && previewStage) {
        stageInput.addEventListener("input", () => {
            previewStage.textContent = stageInput.value.trim() ? `★ ${stageInput.value}` : "No Stage Name";
        });
    }

    if (bioInput && previewBio) {
        bioInput.addEventListener("input", () => {
            previewBio.textContent = bioInput.value.trim() || "No bio entered yet.";
        });
    }

    if (districtSelect && previewDistrict) {
        districtSelect.addEventListener("change", () => {
            previewDistrict.textContent = districtSelect.options[districtSelect.selectedIndex].text;
        });
    }
});