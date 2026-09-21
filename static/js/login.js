document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.querySelector(".btn-pwd-toggle");
    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            const pwdInput = document.getElementById("login-password");
            if (!pwdInput) return;
            if (pwdInput.type === "password") {
                pwdInput.type = "text";
                toggleBtn.textContent = "HIDE";
            } else {
                pwdInput.type = "password";
                toggleBtn.textContent = "SHOW";
            }
        });
    }
});