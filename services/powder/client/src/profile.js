import React, { Component } from 'react';

import Paper from 'material-ui/Paper';
import TextField from 'material-ui/TextField';
import FlatButton from 'material-ui/FlatButton';

import { connect } from 'react-redux'
import { changeTextField } from './actions'

export class Profile extends Component {
    constructor(props) {
        super(props);
        this.state = {imageUrl: 'http://static1.businessinsider.com/image/5228c23beab8ea9c4f8b456b/7- ways-companies-deter-women-in-tech-jobs.jpg'}
    }

    imageChange = (e) => {
        e.preventDefault()

        let reader = new FileReader();
        let file = e.target.files[0]

        reader.onloadend = () => {
            this.setState({
                imageUrl: reader.result
            })
        }
        
        reader.readAsDataURL(file)
    }

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
                src={this.state.imageUrl}
                alt=""
                onClick={() => {this.imageInput.click()}}
            />
            <input
                ref={input => this.imageInput = input}
                type="file"
                style={{display: 'none'}}
                onChange={this.imageChange}
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
        }
    }
})(Profile)
