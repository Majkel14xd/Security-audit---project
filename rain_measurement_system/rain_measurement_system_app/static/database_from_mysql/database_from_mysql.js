document.addEventListener("DOMContentLoaded", function () {
  const table = document.getElementById("table_data");
  const prevButton = document.getElementById("prevPage");
  const nextButton = document.getElementById("nextPage");

  const rowsPerPage = 7;
  let currentPage = 1;

  function displayPage(page) {
    const startIndex = (page - 1) * rowsPerPage;
    const endIndex = page * rowsPerPage;

    for (let i = 1; i < table.rows.length; i++) {
      if (i > startIndex && i <= endIndex) {
        table.rows[i].style.display = "table-row";
      } else {
        table.rows[i].style.display = "none";
      }
    }
  }

  prevButton.addEventListener("click", function () {
    if (currentPage > 1) {
      currentPage--;
      displayPage(currentPage);
    }
  });

  nextButton.addEventListener("click", function () {
    const totalPages = Math.ceil((table.rows.length - 1) / rowsPerPage);
    if (currentPage < totalPages) {
      currentPage++;
      displayPage(currentPage);
    }
  });

  displayPage(currentPage);
});
