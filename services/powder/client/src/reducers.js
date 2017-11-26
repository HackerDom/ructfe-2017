import { combineReducers } from 'redux';
import update from 'immutability-helper'

import {
    OPEN_DIALOG,
    CLOSE_DIALOG
} from './actions'

const initialState = {
    dialogs: {
        auth: false
    },
    changes: {
        auth: {
            login: {
                login: '',
                password: '',
            },
            signup: {
                login: '',
                password: '',
            }
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

export const doReduce = combineReducers({
    dialogs
})
