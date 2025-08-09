document.addEventListener("DOMContentLoaded", function () {
    fetch("navbar.html")
        .then(res => res.text())
        .then(data => {
            document.getElementById("navbar").innerHTML = data;
        });
});