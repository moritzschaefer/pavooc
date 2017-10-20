import * as React from "react";
import { withRouter } from "react-router";
import { Route } from "react-router";
import { MuiThemeProvider, createMuiTheme } from "material-ui/styles";

import Initial from "../Initial";
import KnockoutList from "../KnockoutList";
import GeneViewer from "../GeneViewer";
import Messages from "../Messages";

const theme = createMuiTheme();

class App extends React.Component {
  render() {
    return (
      <MuiThemeProvider theme={theme}>
        <div className="App">
          <div className="AppHeader">
            <h1>PAVOOC</h1>
          </div>
          <div className="AppBody">
            <Route exact={true} path="/" component={Initial} />
            <Route path="/knockout" component={KnockoutList} />
            <Route path="/geneviewer/:geneId" component={GeneViewer} />
          </div>
          <Messages />
        </div>
      </MuiThemeProvider>
    );
  }
}

export default withRouter(App);
