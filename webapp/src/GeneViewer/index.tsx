import * as React from "react";
import { connect } from "react-redux";
import { push } from "react-router-redux";

import Button from "material-ui/Button";
import Input, { InputLabel } from "material-ui/Input";
import { MenuItem } from "material-ui/Menu";
import { FormControl } from "material-ui/Form";
import Select from "material-ui/Select";

import ProteinViewer from "./ProteinViewer";
import SequenceViewer from "./SequenceViewer";
import GuideTable from "./GuideTable";
import { setGuideCount } from "./actions";
import "./style.css";

interface GeneData {
  gene_id: string;
  guides: Array<any>;
  pdbs: Array<any>;
}

interface Props {
  geneId: string;
  guideCount: number;
  setGuideCount: (event: any) => {};
  geneData: GeneData;
  push: (route: string) => {};
}

interface State {
  selectedPdb: number;
}

class GeneViewer extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {selectedPdb: 0};
  }
  render() {
    const { guideCount, geneData, geneId } = this.props;
    const { selectedPdb } = this.state;
    return (
      <div className="mainContainer">
        <div className="containerTop">
          <div className="geneViewerHeader">
            <Button onClick={() => this.props.push("/knockout")} raised={true} className="backButton">Back</Button>
          </div>
          <h2 className="heading">{geneId}</h2>
          <div className="topControls">
            <FormControl>
              <InputLabel htmlFor="guides-count">Guides per gene</InputLabel>
               <Select
                value={guideCount}
                onChange={this.props.setGuideCount}
                input={<Input id="guides-count" />}
                MenuProps={{
                              PaperProps: {
                                style: {
                                  maxHeight: 200
                                },
                              },
                            }}
              >
                {Array.from(new Array(10), (_: {}, i: number) => (
                  <MenuItem value={i} key={i}>
                    {i}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Button raised={true}>&darr; CSV</Button>
          </div>
        </div>
        <div className="containerCenter">
          <ProteinViewer className="proteinViewer" pdb={geneData.pdbs[selectedPdb]}/>
          <GuideTable guides={geneData.guides} className="guideTable"/>
        </div>
        <div className="containerBottom">
          <SequenceViewer />
        </div>
      </div>
    );
  }
}

const mapStateToProps = (
  state: any,
  { match: { params: { geneId } } }: { match: { params: { geneId: string } } }
) => ({
  guideCount: state.geneViewer.guideCount,
  geneData: state.io.guides.find((v: any) => v.gene_id === geneId),
  geneId
});

const mapDispatchToProps = (dispatch: any) => ({
  setGuideCount: (event: any) => dispatch(setGuideCount(event.target.value)),
  push: (route: string) => dispatch(push(route))
});

export default connect(mapStateToProps, mapDispatchToProps)(GeneViewer);
