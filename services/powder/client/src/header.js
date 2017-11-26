import React, { Component } from 'react';
import AppBar from 'material-ui/AppBar';
import FlatButton from 'material-ui/FlatButton';

import { connect } from 'react-redux'

import { openDialog } from './actions'

export class Header extends Component {
    render() {
        return <AppBar
                    title='Powder'
					iconElementRight={
                    	<FlatButton
                        	label="Login"
		                    onClick={this.props.onLoginButtonClick}
						/>
					}
               />
    }
}
Header = connect(null, (dispatch) => {
	return {onLoginButtonClick: () => {dispatch(openDialog('auth'))}}
})(Header)
