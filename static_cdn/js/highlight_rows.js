document.addEventListener('DOMContentLoaded', function () {
    // Находим все строки таблицы
    const rows = document.querySelectorAll('#result_list tbody tr');

    rows.forEach(row => {
        // Получаем ID объекта из атрибута data-order-id
        const orderId = row.dataset.orderId;

        if (!orderId) {
            return; // Пропускаем строки без ID
        }

        // Выполняем AJAX-запрос для получения данных о заказе
        fetch(`/admin/api/order/${orderId}/`)
            .then(response => response.json())
            .then(data => {
                // Проверяем условия подсветки
                if (data.check_call && data.comment.trim() !== '') {
                    row.classList.add('row-highlight');
                }
            })
            .catch(error => console.error('Ошибка при получении данных:', error));
    });
});