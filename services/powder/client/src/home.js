import React, { Component } from 'react';

import { CardHeader, CardMedia, Card } from 'material-ui/Card';
import FlatButton from 'material-ui/FlatButton';
import Paper from 'material-ui/Paper';
import { Toolbar, ToolbarGroup } from 'material-ui/Toolbar';

export class Home extends Component {

    render() {
        let style = {
            width: '60%',
            'marginTop': 50,
            'marginLeft': 'auto',
            'marginRight': 'auto',
        }
        return <Paper style={style}>
                <Card>
                <CardHeader
                    title="Some Body"
                    subtitle="nickname"
                />
                <CardMedia>
                    <img
                        src="http://static1.businessinsider.com/image/5228c23beab8ea9c4f8b456b/7-ways-companies-deter-women-in-tech-jobs.jpg"
                        alt=""
                    />
                </CardMedia>
                    <Toolbar>
                        <ToolbarGroup>
                            <FlatButton label="Like!"/>
                        </ToolbarGroup>
                        <ToolbarGroup>
                            <FlatButton label="Next"/>
                        </ToolbarGroup>
                    </Toolbar>
            </Card>
        </Paper>
    }
}
