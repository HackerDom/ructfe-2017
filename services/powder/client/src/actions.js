export const OPEN_DIALOG = 'OPEN_DIALOG'
export const CLOSE_DIALOG = 'CLOSE_DIALOG'

export const CHANGE_TEXT_FIELD = 'CHANGE_TEXT_FIELD'

export const START_LOGIN = 'START_LOGIN'
export const SUCCESS_LOGIN = 'SUCCESS_LOGIN'
export const FAILED_LOGIN = 'FAILED_LOGIN'

export const START_SIGNUP = 'START_SIGNUP'
export const SUCCESS_SIGNUP = 'SUCCESS_SIGNUP'
export const FAILED_SIGNUP = 'FAILED_SIGNUP'

export const SHOW_NOTIFICATIONS = 'SHOW_NOTIFICATIONS'
export const HIDE_NOTIFICATIONS = 'HIDE_NOTIFICATIONS'

export const LOGOUT = 'LOGOUT'

export function openDialog(name) {
    return {
        type: OPEN_DIALOG,
        name: name
    }
}

export function closeDialog(name) {
    return {
        type: CLOSE_DIALOG,
        name: name
    }
}

export function changeTextField(group, name, value) {
    return {
        type: CHANGE_TEXT_FIELD,
        group: group,
        name: name,
        value: value
    }
}

export function startLogin() {
    return {
        type: START_LOGIN
    }
}
export function successLogin(response) {
    return {
        type: SUCCESS_LOGIN,
        response: response
    }
}
export function failedLogin(response) {
    return {
        type: FAILED_LOGIN
    }
}

export function startSignUp() {
    return {
        type: START_SIGNUP
    }
}
export function successSignUp(response) {
    return {
        type: SUCCESS_SIGNUP
    }
}
export function failedSignUp(response) {
    return {
        type: FAILED_SIGNUP
    }
}


export function tryLogin(login, password) {
    return function (dispatch) {
        dispatch(startLogin())

        let form = new FormData()
        form.append('login', login)
        form.append('password', password)

        return fetch("/api/v1/auth/login", {
            method: "POST",
            body: form
        })
        .then(response => response.json())
        .then(json => {
            if (json.error) {
                dispatch(showNotifications(json.errorMessage))
                dispatch(failedLogin(json))
            } else {
                dispatch(showNotifications('OK'))
                dispatch(successLogin(json))
                dispatch(closeDialog('auth'))
            }
        })
    }
}

export function trySignUp(login, password) {
    return function (dispatch) {
        dispatch(startSignUp())

        let form = new FormData()
        form.append('login', login)
        form.append('password', password)

        return fetch("/api/v1/auth/signup", {
            method: "POST",
            body: form
        })
        .then(response => response.json())
        .then(json => {
            if (json.error) {
                dispatch(showNotifications(json.errorMessage))
                dispatch(failedSignUp(json))
            } else {
                dispatch(showNotifications('OK'))
                dispatch(successSignUp(json))
                dispatch(successLogin(json))
                dispatch(closeDialog('auth'))
            }
        })
    }
}

export function showNotifications(text) {
    return {
        type: SHOW_NOTIFICATIONS,
        text: text
    }
}

export function hideNotifications() {
    return {
        type: HIDE_NOTIFICATIONS
    }
}

export function logout() {
    return {
        type: LOGOUT
    }
}
