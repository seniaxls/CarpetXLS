document.addEventListener("DOMContentLoaded", function () {
    // Находим все строки таблицы
    const rows = document.querySelectorAll("#result_list tbody tr");

    rows.forEach(row => {
        // Находим ячейку с номером заказа
        const orderNumberCell = row.querySelector(".field-order_number_with_conditions span");

        if (orderNumberCell) {



            if (orderNumberCell.dataset.shouldHighlight === "true") {

                const checkCallCell = row.querySelector(".field-check_call");
                if (checkCallCell) {
                    // Перекрашиваем только ячейку field-check_call
                    checkCallCell.style.backgroundColor = "#ffdbdc"; // Светло-зеленый фон
                }
            }
            if (orderNumberCell.dataset.shouldHighlight2 === "true") {

                const checkCallCell = row.querySelector(".field-formatted_created_at");
                if (checkCallCell) {
                    // Перекрашиваем только ячейку field-check_call
                    checkCallCell.style.backgroundColor = "#fff5db"; // Светло-зеленый фон
                }
            }

        } else {
            console.error("Order number cell not found in row:", row);
        }
    });
});