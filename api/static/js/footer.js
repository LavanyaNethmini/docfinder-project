document.addEventListener("DOMContentLoaded", function () {
    fetch("/static/footer.html")
        .then(res => res.text())
        .then(data => {
            document.getElementById("footer").innerHTML = data;
        });

});
