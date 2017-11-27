import React, { Component } from 'react';

import AppBar from 'material-ui/AppBar';
import FlatButton from 'material-ui/FlatButton';
import IconMenu from 'material-ui/IconMenu';
import MenuItem from 'material-ui/MenuItem';
import IconButton from 'material-ui/IconButton';
import MoreVertIcon from 'material-ui/svg-icons/navigation/more-vert';

import { connect } from 'react-redux'

import { openDialog } from './actions'

export class Header extends Component {
    render() {
        let iconRight = null
        if (this.props.user.authorized) {
            iconRight = <div>
                <IconMenu
                    iconButtonElement={<IconButton><MoreVertIcon /></IconButton>}
                    anchorOrigin={{horizontal: 'right', vertical: 'top'}}
                    targetOrigin={{horizontal: 'right', vertical: 'top'}}
                >
                    <MenuItem primaryText="Profile"/>
                    <MenuItem
                        primaryText="Sign out"
                        onClick={() => {alert(1)}}
                     />
                </IconMenu>
            </div>
        } else {
            iconRight = <FlatButton
                label="Login"
                onClick={this.props.onLoginButtonClick}
            />
        }

        return <AppBar
                    title='Powder'
                    iconElementRight={iconRight}
                    showMenuIconButton={false}
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
