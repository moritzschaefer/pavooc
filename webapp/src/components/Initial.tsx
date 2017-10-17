import * as React from 'react';
import './Initial.css';
import InitialForm from '../containers/InitialForm';

export interface Props {
  geneIds: Array<string>;
  celllines: Array<string>;
}

export default class Initial extends React.Component<Props, object> {
  render() {
    return (
      <div className="App">
        <div className="AppHeader">
          <h1>PAVOOC</h1>
        </div>
        <div className="AppBody">
          <div className="bodyLeft">
            <p className="teaser">Design and control cutting-edge-scored sgRNAs in an eye-blink</p>
          </div>
          <InitialForm className="bodyRight"/>
        </div>
      </div>
    );
  }
}
