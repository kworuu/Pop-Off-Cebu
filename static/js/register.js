document.addEventListener("DOMContentLoaded", () => {
    // 1. Password Visibility Toggle
    const toggleBtns = document.querySelectorAll(".btn-pwd-toggle");
    toggleBtns.forEach((btn) => {
        btn.addEventListener("click", () => {
            const targetId = btn.getAttribute("data-target");
            const targetInput = document.getElementById(targetId);
            if (!targetInput) return;

            if (targetInput.type === "password") {
                targetInput.type = "text";
                btn.textContent = "HIDE";
            } else {
                targetInput.type = "password";
                btn.textContent = "SHOW";
            }
        });
    });

    // 2. Client-side Realtime Email Format Check
    const emailInput = document.getElementById("reg-email");
    const emailMsg = document.getElementById("email-validation-msg");
    if (emailInput && emailMsg) {
        emailInput.addEventListener("input", () => {
            const val = emailInput.value.trim();
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!val) {
                emailMsg.textContent = "";
            } else if (emailRegex.test(val)) {
                emailMsg.textContent = "✓ Valid email format";
                emailMsg.style.color = "var(--green-utb)";
            } else {
                emailMsg.textContent = "✗ Invalid email address";
                emailMsg.style.color = "var(--rust-accent)";
            }
        });
    }

    // 3. Password Match Indicator
    const p1 = document.getElementById("reg-password");
    const p2 = document.getElementById("reg-confirm-password");
    const matchMsg = document.getElementById("password-match-msg");
    if (p1 && p2 && matchMsg) {
        const checkMatch = () => {
            if (!p2.value) {
                matchMsg.textContent = "";
                return;
            }
            if (p1.value === p2.value) {
                matchMsg.textContent = "✓ Passwords match";
                matchMsg.style.color = "var(--green-utb)";
            } else {
                matchMsg.textContent = "✗ Passwords do not match";
                matchMsg.style.color = "var(--rust-accent)";
            }
        };
        p1.addEventListener("input", checkMatch);
        p2.addEventListener("input", checkMatch);
    }
});