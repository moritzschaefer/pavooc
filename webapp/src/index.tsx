/// <reference path='../types/index.d.ts'/>
import "rxjs"; // import all operators. though: slow
import * as React from "react";
import * as ReactDOM from "react-dom";
import { createStore, combineReducers, applyMiddleware, compose } from "redux";
import { Provider } from "react-redux";
import { persistStore, persistReducer, createTransform } from "redux-persist";
import storage from "redux-persist/es/storage";
import { PersistGate } from "redux-persist/es/integration/react";
import {
  ConnectedRouter,
  routerReducer,
  routerMiddleware
} from "react-router-redux";
import { createEpicMiddleware, combineEpics } from "redux-observable";
import createHistory from "history/createBrowserHistory";

import registerServiceWorker from "./registerServiceWorker";
import "./index.css";

import App from "./App";
import Loading from "./util/Loading";

import IOEpic from "./IO/epic";
import IOReducer from "./IO/reducer";
import MessagesReducer from "./Messages/reducer";
import AppReducer from "./App/reducer";

// Create a history of your choosing (we're using a browser history in this case)
const history = createHistory();

// Build the middleware for intercepting and dispatching navigation actions

const rootReducer = combineReducers({
  router: routerReducer,
  io: IOReducer,
  messages: MessagesReducer,
  app: AppReducer,
});

const epics = combineEpics(IOEpic);
const middleware = applyMiddleware(
  routerMiddleware(history),
  createEpicMiddleware(epics)
);

const mapTransform = createTransform(
  (inboundState: any, key: any) => {
    // convert Map to Array
    let genes = new Array<any>();
    inboundState.genes.forEach((gene_symbol: string, gene_id: string) => genes.push({ gene_id, gene_symbol }));
    return { ...inboundState, genes };
  },
  // transform state being rehydrated
  (outboundState: any, key: any) => {
    let genes = new Map(outboundState.genes.map((g: any) => [g.gene_id, g.gene_symbol]))
    return { ...outboundState, genes };
  },
  // define which reducers this transform gets called for.
  { whitelist: ['io'] }
);

const config = {
  key: "root", // key is required
  transforms: [mapTransform],
  storage // storage is now required
};
// interface Window { [key: string]: any }

const composeEnhancers: any = window['__REDUX_DEVTOOLS_EXTENSION_COMPOSE__'] || compose;

const reducer = persistReducer(config, rootReducer);

// Add the reducer to your store on the `router` key
// Also apply our middleware for navigating
const store = createStore(reducer, composeEnhancers(middleware));

let persistor = persistStore(store);

// Now you can dispatch navigation actions from anywhere!
// store.dispatch(push('/foo'))

// Create an enhanced history that syncs navigation events with the store
ReactDOM.render(
  <Provider store={store}>
    <PersistGate persistor={persistor} loading={<Loading />}>
      {/* ConnectedRouter will use the store from Provider automatically */}
      <ConnectedRouter history={history}>
        <App />
      </ConnectedRouter>
    </PersistGate>
  </Provider>,
  document.getElementById("root") as HTMLElement
);
registerServiceWorker();
