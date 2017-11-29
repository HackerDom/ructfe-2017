import React, { Component } from 'react';

import TextField from 'material-ui/TextField';
import Paper from 'material-ui/Paper';

import { connect } from 'react-redux'
import { submitChat, changeTextField } from './actions'

export class Chat extends Component {
    render() {
        return  <Paper style={{
                                marginTop: '50px',
                                marginLeft: 'auto',
                                marginRight: 'auto',
                                width: '60%',
                                textAlign: 'center'
                             }}
                >
                    <div style={{height: '70vh', display: 'block', textAlign: 'left', marginLeft: 20, paddingTop: 20}}>
                        {(this.props.conversations[this.props.history.location.pathname] || []).map((text) => (
                            <div>text</div>                                                           
                        ))}
                    </div>
                    <form onSubmit={this.props.onChatSubmit(this.props.history.location.pathname)}>
                    <TextField
                        style={{width: '90%'}}
                        floatingLabelText="Message"
                        fullWidth={true}
                        onChange={this.props.onChangeTextField(this.props.history.location.pathname)}
                    />
                    </form>
                </Paper>
    }
}
Chat = connect(
(state) => {
    return {conversations: state.conversations}
},
(dispatch) => {
    return {
        onChangeTextField: (name) => {
            return (e) => {dispatch(changeTextField('chat', name, e.target.value))}
        },
        onChatSubmit: (name) => {
            return (e) => {e.preventDefault(); dispatch(submitChat(name))}
        }
    }
})(Chat)
