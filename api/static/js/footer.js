document.addEventListener("DOMContentLoaded", function () {
    fetch("/templates/footer.html")
        .then(res => res.text())
        .then(data => {
            document.getElementById("footer").innerHTML = data;
        });

});

