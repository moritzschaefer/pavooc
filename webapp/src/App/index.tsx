import * as React from "react";
import { withRouter } from "react-router";
import { Route } from "react-router";
import { MuiThemeProvider, createMuiTheme } from "material-ui/styles";

import Initial from "../Initial";
import KnockoutList from "../KnockoutList";
import KnockoutViewer from "../GeneViewer/KnockoutViewer";
import EditViewer from "../GeneViewer/EditViewer";
import Messages from "../Messages";

const theme = createMuiTheme();

class App extends React.Component {
  render() {
    return (
      <MuiThemeProvider theme={theme}>
        <div className="fullContainer">
          <Route exact={true} path="/" component={Initial} />
          <Route path="/knockout" component={KnockoutList} />
          <Route path="/geneviewer/:geneId" component={KnockoutViewer} />
          <Route path="/edit/:geneId" component={EditViewer} />
          <Messages />
        </div>
    </MuiThemeProvider>
    );
  }
}

export default withRouter(App);
