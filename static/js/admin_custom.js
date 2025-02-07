document.addEventListener("DOMContentLoaded", function () {
    // Находим все строки таблицы
    const rows = document.querySelectorAll("#result_list tbody tr");

    rows.forEach(row => {
        // Находим ячейку с номером заказа
        const orderNumberCell = row.querySelector(".field-order_number_with_conditions span");

        if (orderNumberCell) {
            console.log("Order number:", orderNumberCell.textContent);
            console.log("Should highlight:", orderNumberCell.dataset.shouldHighlight);

            // Проверяем значение атрибута data-should-highlight
            if (orderNumberCell.dataset.shouldHighlight === "true") {
                // Находим ячейку с классом field-check_call
                const checkCallCell = row.querySelector(".field-check_call");

                if (checkCallCell) {
                    // Перекрашиваем только ячейку field-check_call
                    checkCallCell.style.backgroundColor = "#ffdbdc"; // Светло-зеленый фон
                }
            }
        } else {
            console.error("Order number cell not found in row:", row);
        }
    });
});