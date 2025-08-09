document.addEventListener("DOMContentLoaded", function () {
    fetch("/templates/navbar.html")
        .then(res => res.text())
        .then(data => {
            document.getElementById("navbar").innerHTML = data;
        });

});

