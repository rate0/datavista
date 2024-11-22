document.addEventListener('DOMContentLoaded', function () {
    const updateButtonNavbar = document.getElementById('updateButtonNavbar');
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    const successModal = new bootstrap.Modal(document.getElementById('successModal'));

    if (updateButtonNavbar) {
        updateButtonNavbar.addEventListener('click', function (e) {
            e.preventDefault(); 
            updateButtonNavbar.classList.add('disabled');
            loadingModal.show();
            fetch('/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'started') {
                    const interval = setInterval(() => {
                        fetch('/check_update')
                            .then(res => res.json())
                            .then(statusData => {
                                if (statusData.status === 'completed') {
                                    clearInterval(interval);
                                    loadingModal.hide();
                                    successModal.show();
                                    updateButtonNavbar.classList.remove('disabled');
                                    location.reload();
                                }
                            })
                            .catch(err => {
                                console.error('Ошибка при проверке статуса обновления:', err);
                                clearInterval(interval);
                                loadingModal.hide();
                                updateButtonNavbar.classList.remove('disabled');
                            });
                    }, 2000);
                } else if (data.status === 'already_in_progress') {
                    loadingModal.hide();
                    alert('Обновление данных уже выполняется.');
                    updateButtonNavbar.classList.remove('disabled');
                } else {
                    loadingModal.hide();
                    alert('Не удалось начать обновление данных.');
                    updateButtonNavbar.classList.remove('disabled');
                }
            })
            .catch(error => {
                console.error('Ошибка при обновлении данных:', error);
                loadingModal.hide();
                alert('Произошла ошибка при обновлении данных.');
                updateButtonNavbar.classList.remove('disabled');
            });
        });
    }
});
