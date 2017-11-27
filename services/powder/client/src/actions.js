export const OPEN_DIALOG = 'OPEN_DIALOG'
export const CLOSE_DIALOG = 'CLOSE_DIALOG'

export const CHANGE_TEXT_FIELD = 'CHANGE_TEXT_FIELD'

export const START_LOGIN = 'START_LOGIN'
export const SUCCESS_LOGIN = 'SUCCESS_LOGIN'
export const FAILED_LOGIN = 'FAILED_LOGIN'

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
        type: SUCCESS_LOGIN
    }
}
export function failedLogin(response) {
    return {
        type: FAILED_LOGIN
    }
}

export function tryLogin() {
    return function (dispatch) {
        dispatch(startLogin())

        return fetch("/api/v1/token", {method: "POST"})
        .then(response => response.json())
        .then(json => {
            dispatch(successLogin(json))
        })
    }
}
