import React, { Component } from 'react';
import { HashRouter } from 'react-router-dom';

import { Header } from './header'
import { Page } from './page'
import { Notifications } from './notifications'

export class App extends Component {
    render() {
        return (
                <div>
                    <Header/>
                    <HashRouter>
                        <Page/>
                    </HashRouter>
                    <Notifications/>
                </div>
        );
    }
}
