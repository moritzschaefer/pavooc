import * as React from "react";
import * as NGL from "ngl";

interface State {
  stage: typeof NGL.Stage | undefined;
}

interface Props {
  className: string;
  pdb: any;
}

let viewport: any = undefined;

export default class ProteinViewer extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
  }
  componentDidMount() {
    // set up ngl
    const stage = new NGL.Stage(viewport);
    stage.setParameters({ backgroundColor: "white" });
    if (this.props.pdb) {
      stage.loadFile(`rcsb://${this.props.pdb.PDB}`, { defaultRepresentation: true });
    }

    this.setState({ stage });
  }
  render() {
    return (
      <div className={this.props.className}>
        <div
          ref={(v: any) => {
            viewport = v;
          }}
          style={{ flex: 1 }}
        />
      </div>
    );
  }
}
