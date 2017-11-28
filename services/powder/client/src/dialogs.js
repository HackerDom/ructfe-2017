import React, { Component } from 'react';

import {Tabs, Tab} from 'material-ui/Tabs';
import Dialog from 'material-ui/Dialog';
import FlatButton from 'material-ui/FlatButton';
import TextField from 'material-ui/TextField';

import { connect } from 'react-redux'
import { closeDialog, changeTextField, tryLogin, trySignUp } from './actions'

export class AuthDialog extends Component {
    render() {
        let dialogTabs = [
            <Tabs key='tabs'>
                <Tab label="Login">
                    <TextField
                        fullWidth={true}
                        floatingLabelText="Username"
                        onChange={this.props.onChangeTextField('loginLogin')}
                    />
                    <TextField
                        fullWidth={true}
                        floatingLabelText="Password"
                        type="password"
                        onChange={this.props.onChangeTextField('loginPassword')}
                    />
                    <br/>
                    <FlatButton
                        label="Login"
                        fullWidth={true}
                        onClick={this.props.onLoginButtonClick}
                    />
                </Tab>
                <Tab label="Sign up">
                    <TextField
                        fullWidth={true}
                        floatingLabelText="Username"
                        onChange={this.props.onChangeTextField('signupLogin')}
                    />
                    <TextField
                        fullWidth={true}
                        floatingLabelText="Password"
                        type="password"
                        onChange={this.props.onChangeTextField('signupPassword')}
                    />
                    <br/>
                    <FlatButton
                        label="Sign up"
                        fullWidth={true}
                        onClick={this.props.onSignUpButtonClick}
                    />
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
    return {
        open: state.dialogs.auth,
    }
},
(dispatch) => {
    return {
        onCloseAuthDialog: () => {dispatch(closeDialog('auth'))},
        onChangeTextField: (name) => {
            return (e) => {dispatch(changeTextField('auth', name, e.target.value))}
        },
        onLoginButtonClick: () => {dispatch(tryLogin())},
        onSignUpButtonClick: () => {dispatch(trySignUp())},
    }
})(AuthDialog)

export class Dialogs extends Component {
    render() {
        return <AuthDialog/>
    }
}
