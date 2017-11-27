import React, { Component } from 'react';
import { Switch, Route } from 'react-router-dom';

import { Dialogs } from './dialogs'
import { Home } from './home'

export class Page extends Component {
    render() {
        return <div>
            <Dialogs/>
            <Switch>
                <Route exact path="/" component={Home}/>
            </Switch>
        </div>
    }
}
