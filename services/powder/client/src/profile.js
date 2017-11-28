import React, { Component } from 'react';

import Paper from 'material-ui/Paper';
import TextField from 'material-ui/TextField';

export class Profile extends Component {
    render() {
        let style = {
            width: '40%',
            'marginTop': 50,
            'marginLeft': 'auto',
            'marginRight': 'auto',
            'padding': 30
        }
        return <Paper style={style}>
            <TextField
                fullWidth={true}
                floatingLabelText="Name"
                value={"qwer"}
            />
        </Paper>
    }
}
