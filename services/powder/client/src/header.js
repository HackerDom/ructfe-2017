import React, { Component } from 'react';
import { Link } from 'react-router-dom';

import AppBar from 'material-ui/AppBar';
import FlatButton from 'material-ui/FlatButton';
import IconMenu from 'material-ui/IconMenu';
import MenuItem from 'material-ui/MenuItem';
import IconButton from 'material-ui/IconButton';
import MoreVertIcon from 'material-ui/svg-icons/navigation/more-vert';

import { connect } from 'react-redux'

import { withRouter } from 'react-router'

import { loadProfile, openDialog, logout } from './actions'

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
                    <MenuItem
                        containerElement={<Link to='/profile'/>}
                        primaryText="Profile"
                        onClick={this.props.onProfileButtonClick}
                    />
                    <MenuItem
                        primaryText="Sign out"
                        onClick={() => {
                            this.props.history.push('/');
                            this.props.onLogoutButtonClick()
                        }}
                     />
                </IconMenu>
            </div>
        } else {
            iconRight = <FlatButton
                label="Login"
                onClick={this.props.onLoginButtonClick}
            />
        }
        let style = {
            cursor: 'pointer',
            color: 'inherit',
            textDecoration: 'inherit'
        }
        return <AppBar
                    title={<Link
                        style={style}
                        to="/">
                            <span style={style}>Powder</span>
                        </Link>
                    }
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
    return {
        onLoginButtonClick: () => {dispatch(openDialog('auth'))},
        onLogoutButtonClick: () => {dispatch(logout())},
        onProfileButtonClick: () => {dispatch(loadProfile())}
    }
})(Header)
Header = withRouter(Header)
