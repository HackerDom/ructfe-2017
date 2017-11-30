import React, { Component } from 'react';

import Paper from 'material-ui/Paper';
import TextField from 'material-ui/TextField';
import FlatButton from 'material-ui/FlatButton';

import { connect } from 'react-redux'
import { saveProfile, changeTextField, changeProfilePictureAsync } from './actions'

export class Profile extends Component {
    render() {
        let picStyle = {
            maxWidth: '60%',
            maxHeight: '40vh',
            width: 'auto',
            height: 'auto',
            cursor: 'pointer',
        }
        const isMobile = window.innerWidth <= 500;
        let style = null
        if (!isMobile) {
            style = {
                width: '60%',
                'marginTop': 50,
                'marginLeft': 'auto',
                'marginRight': 'auto',
                'padding': 30,
                'paddingBottom': 10
            }
        } else {
            style = {
                width: '90%',
                'marginTop': 50,
                'marginLeft': 'auto',
                'marginRight': 'auto',
                'padding': 30,
                'paddingBottom': 10

            }

        }

       return <Paper style={style}>
            <img
                style={picStyle}
                key={this.props.profile.picture}
                src={this.props.profile.picture}
                alt="Profile"
                onClick={() => {this.imageInput.click()}}
            />
            <input
                ref={input => this.imageInput = input}
                type="file"
                style={{display: 'none'}}
                onChange={this.props.onChangeProfilePicture}
            />
            <TextField
                fullWidth={true}
                floatingLabelText="Nickname"
                value={this.props.user.data.nickname}
                disabled={true}
            />
            <TextField
                fullWidth={true}
                floatingLabelText="Full name"
                value={this.props.profile.fullname}
                onChange={this.props.onChangeTextField('fullname')}
            />
            <TextField
                fullWidth={true}
                floatingLabelText="Address"
                value={this.props.profile.address}
                onChange={this.props.onChangeTextField('address')}
            />

            <FlatButton
                label="Save"
                fullWidth={true}
                onClick={this.props.onSaveProfileClick}
            />
        </Paper>
    }
}
Profile = connect(
(state) => {
    return {
        user: state.user,
        profile: state.changes.profile
    }
},
(dispatch) => {
    return {
        onChangeTextField: (name) => {
            return (e) => {dispatch(changeTextField('profile', name, e.target.value))}
        },
        onChangeProfilePicture: (e) => {
            dispatch(changeProfilePictureAsync(e.target.files))
        },
        onSaveProfileClick: () => {dispatch(saveProfile())}
    }
})(Profile)
