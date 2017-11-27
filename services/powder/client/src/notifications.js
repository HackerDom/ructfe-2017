import React, { Component } from 'react';

import Snackbar from 'material-ui/Snackbar';

import { connect } from 'react-redux'
import { showNotifications, hideNotifications } from './actions'

export class Notifications extends Component {
    render() {
        return  <Snackbar
                    open={this.props.open}
                    message={this.props.message}
                    autoHideDuration={4000}
                    onRequestClose={this.props.onHideNotifications}
                />
    }
}

Notifications = connect(
(state) => {
    return {
        open: state.notifications.open,
        message: state.notifications.message,
    }
},
(dispatch) => {
    return {
        onShowNotifications: (text) => {
            return () => {dispatch(showNotifications(text))}
        },
        onHideNotifications: () => {dispatch(hideNotifications())}
    }
})(Notifications)
