import * as React from "react";
// import * as NGL from "ngl";

interface State {
  viewport: any;
}

interface Props {

}

export default class ProteinViewer extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      viewport: undefined
    };
  }
  componentDidMount() {
    // set up ngl
    // const stage = NGL.Stage(viewport);
    // stage.setParameters({backgroundColor: "white"})
    // stage.loadFile("rcsb://1crn", {defaultRepresentation: true});
  }
  render() {
    return (
      <div>
        <div ref={(viewport: any) => {this.setState({ viewport })}} style={{height: 500}}/>
      </div>
    );
  }
}
