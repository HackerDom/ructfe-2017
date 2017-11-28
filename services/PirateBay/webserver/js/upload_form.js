document.addEventListener("DOMContentLoaded", init, false);
function init() {
    document.querySelector('#upload_file').addEventListener('change', handleFileSelect, false);
}
function handleFileSelect(e) {
    var new_name = e.target.files[0].name;
    if (new_name.length > 45)
        new_name = new_name.substring(0, 45) + "...";
    document.getElementById("mess").innerHTML = new_name;
}
$(document).ready(function(){
    $('form input').change(function () {
        $('form p').text(this.files.length + " file(s) selected");
    });
});

function set_private(checkbox) {
    if (checkbox.checked) {
        document.getElementById('form').setAttribute("action", "upload_private");
    }
    else {
        document.getElementById('form').setAttribute("action", "upload");
    }
}
