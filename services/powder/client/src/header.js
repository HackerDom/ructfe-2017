import React, { Component } from 'react';

import AppBar from 'material-ui/AppBar';
import FlatButton from 'material-ui/FlatButton';
import FloatingActionButton from 'material-ui/FloatingActionButton';
import Avatar from 'material-ui/Avatar';

import { connect } from 'react-redux'

import { openDialog } from './actions'

export class Header extends Component {
    render() {
        let iconRight = null
        if (this.props.user.authorized) {
            iconRight = <FloatingActionButton
                mini={true}
                children={<Avatar>A</Avatar>}
            />
        } else {
            iconRight = <FlatButton
                label="Login"
                onClick={this.props.onLoginButtonClick}
            />
        }

        return <AppBar
                    title='Powder'
                    iconElementRight={iconRight}
               />
    }
}
Header = connect(
(state) => {
    return {user: state.user}
},
(dispatch) => {
    return {onLoginButtonClick: () => {dispatch(openDialog('auth'))}}
})(Header)
