import React from 'react';
import ReactDOM from 'react-dom';
import { HashRouter } from 'react-router-dom';

import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';

import { Provider } from 'react-redux'

import './index.css';
import { App } from './app'
import { doReduce } from './reducers'
import { loadChats, loadUsers, applicationStart, loadProfile } from './actions'

import { createStore, applyMiddleware, compose } from 'redux'
import thunkMiddleware from 'redux-thunk'

import { autoRehydrate, persistStore } from 'redux-persist'

let store = compose(
    applyMiddleware(
        thunkMiddleware),
    autoRehydrate()
)(createStore)(doReduce)

persistStore(store, {}, () => {
    store.dispatch(applicationStart())
    store.dispatch(loadProfile())
    store.dispatch(loadUsers())
    setInterval(() => store.dispatch(loadUsers()), 5000)
    setInterval(() => store.dispatch(loadChats()), 5000)
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
