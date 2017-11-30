export const OPEN_DIALOG = 'OPEN_DIALOG'
export const CLOSE_DIALOG = 'CLOSE_DIALOG'

export const CHANGE_TEXT_FIELD = 'CHANGE_TEXT_FIELD'
export const CHANGE_PROFILE_PICTURE = 'CHANGE_PROFILE_PICTURE'

export const START_LOGIN = 'START_LOGIN'
export const SUCCESS_LOGIN = 'SUCCESS_LOGIN'
export const FAILED_LOGIN = 'FAILED_LOGIN'

export const START_SIGNUP = 'START_SIGNUP'
export const SUCCESS_SIGNUP = 'SUCCESS_SIGNUP'
export const FAILED_SIGNUP = 'FAILED_SIGNUP'

export const SHOW_NOTIFICATIONS = 'SHOW_NOTIFICATIONS'
export const HIDE_NOTIFICATIONS = 'HIDE_NOTIFICATIONS'

export const START_SAVING_PROFILE = 'START_SAVING_PROFILE'
export const SUCCESS_SAVING_PROFILE = 'SUCCESS_SAVING_PROFILE'
export const FAILED_SAVING_PROFILE = 'FAILED_SAVING_PROFILE'

export const START_LOADING_PROFILE = 'START_LOADING_PROFILE'
export const SUCCESS_LOADING_PROFILE = 'SUCCESS_LOADING_PROFILE'
export const FAILED_LOADING_PROFILE = 'FAILED_LOADING_PROFILE'

export const APPLICATION_START = 'APPLICATION_START'

export const START_LOADING_USERS = 'START_LOADING_USERS'
export const SUCCESS_LOADING_USERS = 'SUCCESS_LOADING_USERS'
export const FAILED_LOADING_USERS = 'FAILED_LOADING_USERS'

export const START_SENDING_CHAT = 'START_SENDING_CHAT'
export const SUCCESS_SENDING_CHAT = 'SUCCESS_SENDING_CHAT'
export const FAILED_SENDING_CHAT = 'FAILED_SENDING_CHAT'

export const START_LOADING_CHAT = 'START_LOADING_CHAT'
export const SUCCESS_LOADING_CHAT = 'SUCCESS_LOADING_CHAT'
export const FAILED_LOADING_CHAT = 'FAILED_LOADING_CHAT'

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


export function tryLogin() {
    return function (dispatch, getState) {
        dispatch(startLogin())

        let state = getState()
        let login = state.changes.auth.loginLogin
        let password = state.changes.auth.loginPassword
        let token = state.user.data.token

        let form = new FormData()
        form.append('login', login)
        form.append('password', password)

        return fetch("/api/v1/auth/login", {
            method: "POST",
            body: form,
            headers: new Headers({token: token})
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

export function changeProfilePicture(picture) {
    return {
        type: CHANGE_PROFILE_PICTURE,
        value: picture
    }
}

export function changeProfilePictureAsync(files) {
    return dispatch => {
        let file = files[0];
        let reader = new FileReader();

        reader.onloadend = () => {
            dispatch(changeProfilePicture(reader.result));
        }

        return reader.readAsDataURL(file);
    }
}

export function trySignUp() {
    return function (dispatch, getState) {
        dispatch(startSignUp())

        let state = getState()
        let login = state.changes.auth.signupLogin
        let password = state.changes.auth.signupPassword
        let token = state.user.data.token

        let form = new FormData()
        form.append('login', login)
        form.append('password', password)

        return fetch("/api/v1/auth/signup", {
            method: "POST",
            body: form,
            headers: new Headers({token: token})
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

export function startSavingProfile() {
    return {
        type: START_SAVING_PROFILE
    }
}

export function failedSavingProfile() {
    return {
        type: FAILED_SAVING_PROFILE
    }
}

export function successSavingProfile() {
    return {
        type: SUCCESS_SAVING_PROFILE
    }
}


export function saveProfile() {
    return function (dispatch, getState) {
        let state = getState();
        dispatch(startSavingProfile());

        let form = new FormData();
        form.append('fullname', state.changes.profile.fullname);
        form.append('picture', state.changes.profile.picture);
        form.append('address', state.changes.profile.address);

        let token = state.user.data.token

        return fetch("/api/v1/user/profile", {
            method: "POST",
            body: form,
            headers: new Headers({token: token})
        })
        .then(response => response.json())
        .then(json => {
            if (json.error) {
                dispatch(showNotifications(json.errorMessage))
                dispatch(failedSavingProfile(json))
            } else {
                dispatch(showNotifications('Profile saved succesfully'))
                dispatch(successSavingProfile(json))
            }
        })

    }
}

export function startLoadingProfile() {
    return {
        type: START_LOADING_PROFILE
    }
}

export function failedLoadingProfile() {
    return {
        type: FAILED_LOADING_PROFILE

    }
}

export function successLoadingProfile(response) {
    return {
        type: SUCCESS_LOADING_PROFILE,
        response: response
    }
}


export function loadProfile() {
    return function (dispatch, getState) {
        let state = getState();
        dispatch(startLoadingProfile());
        let token = state.user.data.token

        if (!token) {
            return null
        }

        return fetch("/api/v1/user/profile", {
            method: "GET",
            headers: new Headers({token: token})
        })
        .then(response => response.json())
        .then(json => {
            if (json.error) {
                dispatch(showNotifications(json.errorMessage))
                dispatch(failedLoadingProfile(json))
            } else {
                dispatch(successLoadingProfile(json))
            }
        })

    }
}

export function applicationStart() {
    return {
        type: APPLICATION_START
    }
}

export function loadUsers() {
    return function(dispatch) {
        dispatch(startLoadingUsers());
        return fetch("/api/v1/users", {
            method: "GET",
        })
        .then(response => response.json())
        .then(json => {
            if (json.error) {
                dispatch(showNotifications(json.errorMessage))
                dispatch(failedLoadingUsers(json))
            } else {
                dispatch(successLoadingUsers(json))
            }
        })
    }
}

export function startLoadingUsers() {
    return {
        type: START_LOADING_USERS
    }
}

export function failedLoadingUsers() {
    return {
        type: FAILED_LOADING_USERS
    }
}

export function successLoadingUsers(response) {
    return {
        type: SUCCESS_LOADING_USERS,
        response: response
    }
}

export function startSendingChat() {
    return {
        type: START_SENDING_CHAT
    }
}

export function successSendingChat(response, nickname, message, name) {
    return {
        type: SUCCESS_SENDING_CHAT,
        response: response,
        nickname: nickname,
        message: message,
        name: name         
    }
}

export function failedSendingChat() {
    return {
        type: FAILED_SENDING_CHAT
    }
}

export function submitChat(name) {
    return function(dispatch, getState) {
        let state = getState();
        dispatch(startSendingChat());

        let form = new FormData();
        form.append('to', name)
        form.append('message', state.changes.chat[name]);

        let token = state.user.data.token

        return fetch("/api/v1/conversations", {
            method: "POST",
            body: form,
            headers: new Headers({token: token})
        })
        .then(response => response.json())
        .then(json => {
            if (json.error) {
                dispatch(showNotifications(json.errorMessage))
                dispatch(failedSendingChat(json))
            } else {
                dispatch(successSendingChat(json, state.user.data.nickname, state.changes.chat[name], name))
            }
        })
    }
}

export function startLoadingChat() {
    return {
        type: START_LOADING_CHAT
    }
}

export function successLoadingChat(response) {
    return {
        type: SUCCESS_LOADING_CHAT,
        response: response,
    }
}

export function failedLoadingChat() {
    return {
        type: FAILED_LOADING_CHAT
    }
}

export function loadChat(login) {
    return function (dispatch, getState) {
        let state = getState();

        dispatch(startLoadingChat());

        let token = state.user.data.token

        if (!token) {
            return null
        }

        return fetch("/api/v1/conversations?to=" + login , {
            method: "GET",
            headers: new Headers({token: token})
        })
        .then(response => response.json())
        .then(json => {
            if (json.error) {
                dispatch(showNotifications(json.errorMessage))
                dispatch(failedLoadingChat(json))
            } else {
                dispatch(successLoadingChat(json))
            }
        }).catch(function(error) {
            console.log(error)
        })

    }
}

export function loadChats() {
    return function (dispatch, getState) {
        let state = getState();   
        for (var chat in state.conversations) {
            dispatch(loadChat(chat))
        }
    }
}
