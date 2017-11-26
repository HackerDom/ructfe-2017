import { combineReducers } from 'redux';
import update from 'immutability-helper'

import {
    OPEN_DIALOG,
    CLOSE_DIALOG,
    CHANGE_TEXT_FIELD
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

export const doReduce = combineReducers({
    dialogs,
    user,
    changes
})
