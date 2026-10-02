function openCaseModal() {
    const modal = document.getElementById("caseModal");

    if (modal) {
        modal.classList.add("show");
    }
}


function closeCaseModal() {
    const modal = document.getElementById("caseModal");

    if (modal) {
        modal.classList.remove("show");
    }
}


document.addEventListener("click", function (event) {

    const modal = document.getElementById("caseModal");

    if (!modal) {
        return;
    }

    if (event.target === modal) {
        closeCaseModal();
    }

});


document.addEventListener("keydown", function (event) {

    if (event.key === "Escape") {
        closeCaseModal();
    }

});