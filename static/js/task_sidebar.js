document.addEventListener('DOMContentLoaded', () => {
    const overlay = document.getElementById('sidebar-overlay');
    const container = document.getElementById('sidebar-container');

    document.querySelectorAll('.open-sidebar-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const taskItem = btn.closest('.task-item');

            // 清空 container 並載入 sidebar HTML
            container.innerHTML = '';
            const res = await fetch('/sidebar-template');
            container.innerHTML = await res.text();

            const sidebar = document.getElementById('task-sidebar');
            sidebar.dataset.taskId = taskItem.dataset.id;

            // 填入表單資料
            document.getElementById('sidebar-title').value = taskItem.dataset.title;
            document.getElementById('sidebar-start').value = taskItem.dataset.start;
            document.getElementById('sidebar-end').value = taskItem.dataset.end;
            document.getElementById('sidebar-progress-slider').value = taskItem.dataset.progress;
            document.getElementById('sidebar-progress-number').value = taskItem.dataset.progress;
            document.getElementById('sidebar-status').value = taskItem.dataset.status;
            document.getElementById('sidebar-description').value = taskItem.dataset.description || '';

            overlay.classList.add('active');

            // 延遲觸發 open，確保滑入動畫
            requestAnimationFrame(() => {
                sidebar.classList.add('open');
            });

            initSidebar();
        });
    });

    overlay.addEventListener('click', closeSidebar);
});

function closeSidebar() {
    const sidebar = document.getElementById('task-sidebar');
    const overlay = document.getElementById('sidebar-overlay');

    if (sidebar) sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('active');

    // 可加延遲清空，避免動畫被中斷
    setTimeout(() => {
        if (sidebar) sidebar.remove();
    }, 300); // 與 CSS transition 時間一致
}
function moveTaskCard(taskId, newStatus) {
    const card = document.getElementById(`task-${taskId}`);
    if (!card) return;

    // 目標容器選取
    let container;
    if (newStatus === 'todo') container = document.querySelector('.task-column:nth-child(1) .task-list');
    else if (newStatus === 'doing') container = document.querySelector('.task-column:nth-child(2) .task-list');
    else if (newStatus === 'done') container = document.querySelector('.task-column:nth-child(3) .task-list');
    else if (newStatus === 'pending') container = document.querySelector('.task-column:nth-child(1) .task-list');
    else container = card.parentElement;

    // 將卡片移到新容器
    container.appendChild(card);

    // 更新空狀態訊息
    const columns = document.querySelectorAll('.task-column .task-list');
    columns.forEach(col => {
        const emptyMsg = col.querySelector('.empty-msg');
        if (col.children.length === 0) {
            // 如果沒有任何卡片，顯示訊息
            if (!emptyMsg) {
                const msg = document.createElement('div');
                msg.className = 'empty-msg';
                msg.textContent = '目前沒有任何工作';
                col.appendChild(msg);
            }
        } else {
            // 有卡片就移除訊息
            if (emptyMsg) emptyMsg.remove();
        }
    });
}
function initSidebar() {
    const sidebar = document.getElementById('task-sidebar');
    if (!sidebar) return;

    const slider = document.getElementById('sidebar-progress-slider');
    const number = document.getElementById('sidebar-progress-number');
    const closeBtn = document.getElementById('close-sidebar');
    const saveBtn = document.getElementById('sidebar-save-btn');
    const overlay = document.getElementById('sidebar-overlay');

    // 進度同步
    slider.oninput = () => number.value = slider.value;
    number.oninput = () => {
        let val = Math.min(100, Math.max(0, Number(number.value) || 0));
        number.value = val;
        slider.value = val;
    };

    closeBtn.onclick = closeSidebar;

    saveBtn.onclick = async (e) => {
        e.preventDefault();

        const taskId = sidebar.dataset.taskId;
        const form = sidebar.querySelector('form');
        const formData = new FormData(form);

        try {
            const res = await fetch(`/update/${taskId}`, {
                method: 'POST',
                body: formData,
                credentials: 'include'
            });

            if (!res.ok) {
                const msg = await res.text();
                alert('更新失敗: ' + msg);
                return;
            }

            // 後端回傳最新資料
            const updatedTask = await res.json();

            // 找到對應 taskItem
            const taskItem = document.querySelector(`.task-item[data-id="${taskId}"]`);
            if (taskItem) {
                // 先更新 dataset
                taskItem.dataset.title = updatedTask.title;
                taskItem.dataset.start = updatedTask.start_at;
                taskItem.dataset.end = updatedTask.end_at;
                taskItem.dataset.progress = updatedTask.progress;
                taskItem.dataset.status = updatedTask.status;
                taskItem.dataset.description = updatedTask.description;

                // 更新文字內容
                taskItem.querySelector('.card-title').textContent = updatedTask.title;
                taskItem.querySelector('.date-title').textContent =
                    updatedTask.start_at + ' - ' + updatedTask.end_at;
                taskItem.querySelector('.progress-value').textContent = updatedTask.progress + '%';
                taskItem.querySelector('.progress-bar').style.width = updatedTask.progress + '%';

                // 狀態文字更新，放在 dataset 更新之後
                const statusLabel = taskItem.querySelector('.status-badge');
                if (statusLabel) {
                    // 先確認後端回傳值對應前端字串
                    const statusTextMap = {
                        todo: 'Todo',
                        doing: 'Doing',
                        done: 'Done',
                        pending: 'Pending'
                    };
                    const statusKey = updatedTask.status.toLowerCase(); // 避免大小寫不一致
                    statusLabel.textContent = statusTextMap[statusKey] || updatedTask.status;
                    statusLabel.className = 'status-badge ' + statusKey;
                }
                moveTaskCard(taskId, updatedTask.status);
            }

            closeSidebar();
        } catch (err) {
            console.error(err);
            alert('系統錯誤');
        }
    };
}