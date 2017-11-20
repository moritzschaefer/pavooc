import * as React from "react";
import { connect } from "react-redux";
import { push } from "react-router-redux";

import Button from "material-ui/Button";

import { toggleGuideSelection, markGeneEdit } from "../IO/actions";
import ProteinViewer from "./ProteinViewer";
import SequenceViewer from "./SequenceViewer";
import GuideTable from "./GuideTable";
import "./style.css";

export interface GeneData {
  gene_id: string;
  guides: Array<any>;
  pdbs: Array<any>;
}

interface Props {
  geneId: string;
  geneData: GeneData;
  push: (route: string) => {};
  markGeneEdit: (geneId: string) => {};
  toggleGuideSelection: (geneId: string, guideIndex: number) => {};
}

interface State {
  selectedPdb: number;
  hoveredGuide: number | undefined;
}

class GeneViewer extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { selectedPdb: 0, hoveredGuide: undefined };
  }

  guideCheckboxClicked = (guideIndex: number) => {
    const { geneId } = this.props;
    this.props.toggleGuideSelection(geneId, guideIndex);
    this.props.markGeneEdit(geneId);
  }
  setHoveredGuide = (hoveredGuide: number): void => {
    this.setState({ hoveredGuide });
  };

  showPdb = (clickedPdb: string): void => {
    const { geneData } = this.props;
    const selectedPdb = geneData.pdbs.findIndex(
      (pdb: any) => pdb.PDB === clickedPdb
    );
    if (selectedPdb >= 0) {
      this.setState({ selectedPdb });
    } else {
      console.log("Error: selected pdb doesnt exist in genedata");
    }
  };

  render() {
    const { geneData, geneId } = this.props;
    const { selectedPdb, hoveredGuide } = this.state;
    return (
      <div className="mainContainer">
        <div className="containerTop">
          <div className="geneViewerHeader">
            <Button
              onClick={() => this.props.push("/knockout")}
              raised={true}
              className="backButton"
            >
              Back
            </Button>
          </div>
          <h2 className="heading">{geneId}</h2>
          <div className="topControls">
            <Button raised={true}>&darr; CSV</Button>
          </div>
        </div>
        <div className="containerCenter">
          <ProteinViewer
            hoveredGuide={hoveredGuide}
            setHoveredGuide={this.setHoveredGuide}
            className="proteinViewer"
            guides={geneData.guides}
            pdb={geneData.pdbs[selectedPdb]}
          />
          <GuideTable
            hoveredGuide={hoveredGuide}
            setHoveredGuide={this.setHoveredGuide}
            guideClicked={this.guideCheckboxClicked}
            guides={geneData.guides}
            className="guideTable"
          />
        </div>
        <div className="containerBottom">
          <SequenceViewer
            hoveredGuide={hoveredGuide}
            guides={geneData.guides}
            onGuideHovered={this.setHoveredGuide}
            onPdbClicked={this.showPdb}
            gene={geneData}
          />
        </div>
      </div>
    );
  }
}

const mapStateToProps = (
  state: any,
  { match: { params: { geneId } } }: { match: { params: { geneId: string } } }
) => ({
  geneData: state.io.guides.find((v: any) => v.gene_id === geneId),
  geneId
});

const mapDispatchToProps = (dispatch: any) => ({
  push: (route: string) => dispatch(push(route)),
  toggleGuideSelection: (geneId: string, guideIndex: number) => dispatch(toggleGuideSelection(geneId, guideIndex)),
  markGeneEdit: (geneId: string) => dispatch(markGeneEdit(geneId))
});

export default connect(mapStateToProps, mapDispatchToProps)(GeneViewer);
