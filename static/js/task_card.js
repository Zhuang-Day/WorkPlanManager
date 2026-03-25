document.querySelectorAll('.task-item').forEach(task => {
    const slider = task.querySelector('.progress-slider');
    const numberInput = task.querySelector('.progress-number-input');
    const valueDisplay = task.querySelector('.progress-value');
    const progressBar = task.querySelector('.progress-bar');

    function updateProgress(val) {
        val = Math.max(0, Math.min(100, Number(val) || 0));
        if (valueDisplay) valueDisplay.textContent = val + '%';
        if (slider) slider.value = val;
        if (numberInput) numberInput.value = val;
        if (progressBar) progressBar.style.width = val + '%';
    }

    if (slider) {
        slider.addEventListener('input', () => updateProgress(slider.value));
    }

    if (numberInput) {
        numberInput.addEventListener('input', () => updateProgress(numberInput.value));
    }
});