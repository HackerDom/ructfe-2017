import React, { Component } from 'react';

import { Header } from './header'
import { Page } from './page'
import { Notifications } from './notifications'

export class App extends Component {
    render() {
        return (
                <div>
                    <Header/>
                    <Page/>
                    <Notifications/>
                </div>
        );
    }
}
