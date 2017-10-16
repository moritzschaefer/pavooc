import * as React from 'react';

import { MuiThemeProvider, createMuiTheme } from 'material-ui/styles';
import Initial from './components/Initial';


const theme = createMuiTheme();


export default class App extends React.Component {
  render() {
    return (
      <MuiThemeProvider
        theme={theme}
      >
        <Initial geneIds={['ENSG00000251357.4.guides', 'ENSG10000251357.4.guides', 'ENSG00000251352.4.guides', 'ENSG04000251357.4.guides', 'ENSG00a000251357.4.guides', 'ENSG0e0000251357.4.guides']} celllines={['A', 'B', 'CCC', 'AC']} />
      </MuiThemeProvider>
    );
  }
}
