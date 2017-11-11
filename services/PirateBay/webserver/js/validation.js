function validate_login(form) {
    var login = form.elements.login.value;
    if (login.match(/^[a-z0-9_-]{3,16}$/) == null) {
        document.getElementById("login_message").innerHTML = "Login must match regex ^[a-z0-9_-]{3,16}$";
        document.getElementById("submit").disabled = true;
    }
    else {
        document.getElementById("login_message").innerHTML = "";
        document.getElementById("submit").disabled = false;
    }
}
