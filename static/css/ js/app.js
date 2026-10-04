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


/* =========================================================
   AI MARKDOWN
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const answer = document.querySelector(".ai-markdown-answer");

    if (!answer) {
        return;
    }

    if (typeof marked === "undefined") {
        return;
    }

    let markdown = answer.textContent;

    markdown = markdown.replace(/\\\*\\\*/g, "**");
    markdown = markdown.replace(/\\#/g, "#");
    markdown = markdown.replace(/\\-/g, "-");

    answer.innerHTML = marked.parse(markdown);

});