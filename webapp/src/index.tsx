import 'rxjs'; // import all operators. though: slow
import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { createStore, combineReducers, applyMiddleware } from 'redux';
import { Provider } from 'react-redux';
import { Route } from 'react-router';
import { ConnectedRouter, routerReducer, routerMiddleware } from 'react-router-redux'
import { createEpicMiddleware, combineEpics } from 'redux-observable';
import createHistory from 'history/createBrowserHistory'
import { MuiThemeProvider, createMuiTheme } from 'material-ui/styles';

import registerServiceWorker from './registerServiceWorker';
import './index.css';

import Initial from './components/Initial';
import KnockoutList from './components/KnockoutList';

import IOEpic from './IO/epic';
import IOReducer from './IO/reducer';


const theme = createMuiTheme();


// Create a history of your choosing (we're using a browser history in this case)
const history = createHistory();

// Build the middleware for intercepting and dispatching navigation actions

const reducers = combineReducers({
  router: routerReducer,
  io: IOReducer,
});

const epics = combineEpics(IOEpic);
const middleware = applyMiddleware(routerMiddleware(history),
                                   createEpicMiddleware(epics));

// Add the reducer to your store on the `router` key
// Also apply our middleware for navigating
const store = createStore(
  reducers,
  middleware
);

// Now you can dispatch navigation actions from anywhere!
// store.dispatch(push('/foo'))

// Create an enhanced history that syncs navigation events with the store
ReactDOM.render(
  <Provider store={store}>
    { /* ConnectedRouter will use the store from Provider automatically */ }
    <ConnectedRouter history={history}>
      <MuiThemeProvider
        theme={theme}
      >
        <Route exact path="/" component={Initial}/>
        <Route path="/knockout" component={KnockoutList}/>
        {/* <Route path="/topics" component={App}/> */}
        {/* <Initial geneIds={['ENSG00000251357.4.guides', 'ENSG10000251357.4.guides', 'ENSG00000251352.4.guides', 'ENSG04000251357.4.guides', 'ENSG00a000251357.4.guides', 'ENSG0e0000251357.4.guides']} celllines={['A', 'B', 'CCC', 'AC']} /> */}
      </MuiThemeProvider>
    </ConnectedRouter>
  </Provider>,
  document.getElementById('root') as HTMLElement
);
registerServiceWorker();
