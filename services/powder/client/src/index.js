import React from 'react';
import ReactDOM from 'react-dom';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';

import { Provider } from 'react-redux'

import './index.css';
import { App } from './app'
import { doReduce } from './reducers'

import { createStore, applyMiddleware } from 'redux'
import { createLogger } from 'redux-logger'
import thunkMiddleware from 'redux-thunk'

let loggerMiddleware = createLogger()

let store = createStore(
    doReduce,
    applyMiddleware(
        thunkMiddleware,
        loggerMiddleware
))

ReactDOM.render(
<Provider store={store}>
    <MuiThemeProvider>
        <App/>
    </MuiThemeProvider>
</Provider>,
document.getElementById('root'));
