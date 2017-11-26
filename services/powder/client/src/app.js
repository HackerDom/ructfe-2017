import React, { Component } from 'react';

import { Header } from './header'
import { Page } from './page'

export class App extends Component {
    render() {
        return (
                <div>
                    <Header/>
                    <Page/>
                </div>
        );
    }
}
