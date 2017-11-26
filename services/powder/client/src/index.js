import React from 'react';
import ReactDOM from 'react-dom';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';

import { Provider } from 'react-redux'

import './index.css';
import { App } from './app'
import { doReduce } from './reducers'

import { createStore } from 'redux'

let store = createStore(doReduce)

ReactDOM.render(                                                                
<Provider store={store}> 
    <MuiThemeProvider>
        <App/>
    </MuiThemeProvider>
</Provider>,
document.getElementById('root'));  
