import { combineReducers } from 'redux';
import update from 'immutability-helper'

import {
    OPEN_DIALOG,
    CLOSE_DIALOG,
    CHANGE_TEXT_FIELD,
    SHOW_NOTIFICATIONS,
    HIDE_NOTIFICATIONS,
    SUCCESS_LOGIN
} from './actions'

const initialState = {
    user: {
        authorized: false,
        data: {
        }
    },
    dialogs: {
        auth: false
    },
    changes: {
        auth: {
            loginLogin: '',
            loginPassword: '',
            signupLogin: '',
            signupPassword: '',
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
                data: {token: {$set: action.response.token}}
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

export const doReduce = combineReducers({
    dialogs,
    user,
    changes,
    notifications
})
