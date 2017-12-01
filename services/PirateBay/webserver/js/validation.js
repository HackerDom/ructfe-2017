function validate_login(form) {
    var login = form.elements.login.value;
    if (login.match(/^[a-zA-Z0-9_-]{3,50}$/) == null) {
        document.getElementById("error_message").innerHTML = "Login must match regex ^[a-zA-Z0-9_-]{3,50}$";
        document.getElementById("submit").disabled = true;
    }
    else {
        document.getElementById("error_message").innerHTML = "";
        document.getElementById("submit").disabled = false;
    }
}

function validate_password(form) {
    var password = form.elements.password.value;
    if (password.length > 192) {
        document.getElementById("error_message").innerHTML = "Password must be shorter than 193 characters.";
        document.getElementById("submit").disabled = true;
    }
    else {
        document.getElementById("error_message").innerHTML = "";
        document.getElementById("submit").disabled = false;
    }
}
