document.addEventListener("click", (event) => {
    const target = event.target;
    // 判斷點擊的是否是刪除按鈕，且位於 .delete-form 表單中
    if (target.matches(".delete-form button[type='submit']")) {
        const confirmed = confirm("確定要刪除？");
        if (!confirmed) {
            event.preventDefault(); // 阻止表單送出
        }
    }
});