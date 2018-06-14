import * as React from "react";
import "./style.css";
import InitialForm from "./FormContainer";

export interface Props {
  genes: Map<string, string>;
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
            <p className="teaser">
              Design and control cutting-edge-scored sgRNAs in the blink of an eye
            </p>
          </div>
          <InitialForm className="bodyRight" />
        </div>
        <div className="AppFooter">
          <a target="_blank" href="http://pavooc.io/api">API</a> | <a target="_blank" href="https://www.youtube.com/watch?v=XDwK73LI9Vk">Tutorial</a> | <a target="_blank" href="https://github.com/moritzschaefer/pavooc/">GitHub</a> | &copy; 2018 <a href="http://moritzs.de/blog">Moritz Schaefer</a>
        </div>
      </div>
    );
  }
}
