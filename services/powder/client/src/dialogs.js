import React, { Component } from 'react';

import {Tabs, Tab} from 'material-ui/Tabs';
import Dialog from 'material-ui/Dialog';
import FlatButton from 'material-ui/FlatButton';
import TextField from 'material-ui/TextField';

import { connect } from 'react-redux'
import { closeDialog } from './actions'

export class AuthDialog extends Component {
    render() {
        let dialogTabs = [
            <Tabs key='tabs'>
                <Tab label="Login">
                    <TextField fullWidth={true} floatingLabelText="Username"/>
                    <TextField fullWidth={true} floatingLabelText="Password" type="password"/>
                    <br/>
                    <FlatButton label="Login" fullWidth={true}/>
                </Tab>
                <Tab label="Sign up">
                    <TextField fullWidth={true} floatingLabelText="Username"/>
                    <TextField fullWidth={true} floatingLabelText="Password" type="password"/>
                    <br/>
                    <FlatButton label="Sign up" fullWidth={true}/>
                </Tab>
            </Tabs>
        ]
        return (
				<Dialog open={this.props.open}
                        modal={false}
                        onRequestClose={this.props.onCloseAuthDialog}
                        children={dialogTabs}
                />
               )
    }
}
AuthDialog = connect(
(state) => {
    return {open: state.dialogs.auth}
},
(dispatch) => {
	return {onCloseAuthDialog: () => {dispatch(closeDialog('auth'))}}
})(AuthDialog)

export class Dialogs extends Component {
    render() {
        return <AuthDialog/>
    }
}
