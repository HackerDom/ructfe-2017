import React from 'react';
import ReactDOM from 'react-dom';
import { HashRouter } from 'react-router-dom';

import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';

import { Provider } from 'react-redux'

import './index.css';
import { App } from './app'
import { doReduce } from './reducers'
import { applicationStart, loadProfile } from './actions'

import { createStore, applyMiddleware, compose } from 'redux'
import { createLogger } from 'redux-logger'
import thunkMiddleware from 'redux-thunk'

import { autoRehydrate, persistStore } from 'redux-persist'

let loggerMiddleware = createLogger()

let store = compose(
    applyMiddleware(
        thunkMiddleware,
        loggerMiddleware),
    autoRehydrate()
)(createStore)(doReduce)

persistStore(store, {}, () => {
    store.dispatch(applicationStart())
    store.dispatch(loadProfile())
})


ReactDOM.render(
<Provider store={store}>
    <MuiThemeProvider>
        <HashRouter>
            <App/>
        </HashRouter>
    </MuiThemeProvider>
</Provider>,
document.getElementById('root'));
