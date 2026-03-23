document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("form").forEach(form => {
        if (form.method.toUpperCase() === "POST") {
            const input = document.createElement("input");
            input.type = "hidden";
            input.name = "csrf_token";
            input.value = window.CSRF_TOKEN;
            form.appendChild(input);
        }
    });
});