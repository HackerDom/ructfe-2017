export const OPEN_DIALOG = 'OPEN_DIALOG'
export const CLOSE_DIALOG = 'CLOSE_DIALOG'

export const CHANGE_TEXT_FIELD = 'CHANGE_TEXT_FIELD'

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
