import { combineReducers } from 'redux';
import update from 'immutability-helper'

import {
    OPEN_DIALOG,
    CLOSE_DIALOG,
    CHANGE_TEXT_FIELD,
    SHOW_NOTIFICATIONS,
    HIDE_NOTIFICATIONS,
    SUCCESS_LOGIN,
    LOGOUT,
    CHANGE_PROFILE_PICTURE,
    SUCCESS_LOADING_PROFILE,
    SUCCESS_LOADING_USERS,
    FAILED_LOADING_PROFILE,
    APPLICATION_START
} from './actions'

const initialState = {
    user: {
        authorized: false,
        data: {
            token: '',
            nickname: ''
        }
    },
    users: [
    ],
    dialogs: {
        auth: false
    },
    changes: {
        auth: {
            loginLogin: '',
            loginPassword: '',
            signupLogin: '',
            signupPassword: '',
        },
        profile: {
            fullname: '',
            picture: ''
        }
    },
    notifications: {
        open: false,
        message: ''
    }
}

function dialogs(state = initialState.dialogs, action) {
    switch (action.type) {
        case OPEN_DIALOG:
            return update(state, {
                [action.name]: {$set: true}
            })
        case CLOSE_DIALOG:
            return update(state, {
                [action.name]: {$set: false}
            })

        default:
            return state
    }
}

function user(state = initialState.user, action) {
    switch(action.type) {
        case SUCCESS_LOGIN:
            return update(state, {
                authorized: {$set: true},
                data: {
                    token: {$set: action.response.token},
                    nickname: {$set: action.response.nickname}
                },
            })
        case LOGOUT:
            return update(state, {
                authorized: {$set: false},
                data: {
                    token: {$set: ''},
                    nickname: {$set: ''},
                },
            })

        default:
            return state
    }
}

function changes(state = initialState.changes, action) {
    switch(action.type) {
        case CHANGE_TEXT_FIELD:
            return update(state, {
                [action.group]: {[action.name]: {$set: action.value}}
            })
        case CHANGE_PROFILE_PICTURE:
            return update(state, {
                profile: {picture: {$set: action.value}}
            })
        case SUCCESS_LOADING_PROFILE:
            return update(state, {
                profile: {
                    fullname: {$set: action.response.fullname},
                    picture: {$set: action.response.picture},
                }
            })
        case FAILED_LOADING_PROFILE:
            return update(state, {
                profile: {
                    fullname: {$set: ''},
                    picture: {$set: ''},
                },
            })
        case APPLICATION_START:
            return update(state, {
                profile: {
                    fullname: {$set: ''},
                    picture: {$set: ''},
                },
                auth: {
                    loginLogin: {$set: ''},
                    loginPassword: {$set: ''},
                    signupLogin: {$set: ''},
                    signupPassword: {$set: ''},
                }
            })
        default:
            return state
    }
}

function notifications(state = initialState.notifications, action) {
    switch (action.type) {
        case SHOW_NOTIFICATIONS:
            return update(state, {
                open: {$set: true},
                message: {$set: action.text}
            })
        case HIDE_NOTIFICATIONS:
            return update(state, {
                open: {$set: false},
            })
        default:
            return state
    }
}

function users(state = initialState.users, action) {
    switch (action.type) {
        case SUCCESS_LOADING_USERS:
            return update(state, {$set: action.response.users})
        default:
            return state
    }
}

export const doReduce = combineReducers({
    dialogs,
    user,
    changes,
    notifications,
    users
})
