import React, { Component } from 'react';
import { Switch, Route } from 'react-router-dom';

import { Dialogs } from './dialogs'
import { Home } from './home'
import { Profile } from './profile'
import { Chat } from './chat'

export class Page extends Component {
    render() {
        return <div>
            <Dialogs/>
            <Switch>
                <Route exact path="/" component={Home}/>
                <Route exact path="/profile" component={Profile}/>
                <Route path="/chat" component={Chat}/>
            </Switch>
        </div>
    }
}
