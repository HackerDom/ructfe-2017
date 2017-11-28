import React, { Component } from 'react';

import Paper from 'material-ui/Paper';
import TextField from 'material-ui/TextField';
import FlatButton from 'material-ui/FlatButton';

import { connect } from 'react-redux'
import { changeTextField, changeProfilePictureAsync } from './actions'

export class Profile extends Component {
    render() {
        let style = {
            width: '60%',
            'marginTop': 50,
            'marginLeft': 'auto',
            'marginRight': 'auto',
            'padding': 30,
            'paddingBottom': 10

        }
        let picStyle = {
            width: 256,
            cursor: 'pointer',
        }
       return <Paper style={style}>
            <img
                style={picStyle}
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
                    <FlatButton
                        label="Save"
                        fullWidth={true}
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
            changeProfilePictureAsync(e.target.files)
        }
    }
})(Profile)
