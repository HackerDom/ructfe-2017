document.addEventListener("DOMContentLoaded", init, false);
function init() {
    document.querySelector('#upload_file').addEventListener('change', handleFileSelect, false);
}
function handleFileSelect(e) {
    document.getElementById("mess").innerHTML = e.target.files[0].name;
}
$(document).ready(function(){
    $('form input').change(function () {
        $('form p').text(this.files.length + " file(s) selected");
    });
});

function set_private() {
    document.getElementById("form").setAttribute("action", "upload_private")
}