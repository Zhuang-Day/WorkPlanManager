document.addEventListener("click", (event) => {
    const target = event.target;
    if (target.matches("button.btn-danger[type='submit']")) {
        const confirmed = confirm("確定要刪除？");
        if (!confirmed) {
            event.preventDefault();
        }
    }
});