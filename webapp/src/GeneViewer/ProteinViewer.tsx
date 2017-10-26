import * as React from "react";
import * as NGL from "ngl";

interface State {
}

interface Props {
  className: string;
}

let viewport: any = undefined;

export default class ProteinViewer extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
  }
  componentDidMount() {
    // set up ngl
    const stage = new NGL.Stage(viewport);
    stage.setParameters({backgroundColor: "white"})
    stage.loadFile("rcsb://1crn", {defaultRepresentation: true});
  }
  render() {
    return (
      <div className={this.props.className}>
        <div ref={(v: any) => {viewport = v}} style={{flex: 1}}/>
      </div>
    );
  }
}
