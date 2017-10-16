import * as React from 'react';
import './Initial.css';
import InitialForm from './InitialForm';

export interface Props {
  geneIds: Array<string>;
  celllines: Array<string>;
}

export default class Initial extends React.Component<Props, object> {
  render() {
    const { geneIds, celllines } = this.props;
    if (geneIds.length === 0) {
      throw new Error('There are no gene ids to select from.');
    }

    return (
      <div className="App">
        <div className="AppHeader">
          <h1>PAVOOC</h1>
        </div>
        <div className="AppBody">
          <div className="bodyLeft">
            <p className="teaser">Design and control cutting-edge-scored sgRNAs in an eye-blink</p>
          </div>
          <InitialForm className="bodyRight" geneIds={geneIds} celllines={celllines}/>
        </div>
      </div>
    );
  }
}
