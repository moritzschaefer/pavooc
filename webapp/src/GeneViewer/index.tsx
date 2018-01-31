import * as React from "react";
import { connect } from "react-redux";
import { push } from "react-router-redux";

import Button from "material-ui/Button";
import CelllineSelector from "../util/CelllineSelector";

import {
  toggleGuideSelection,
  setGuideSelection,
  markGeneEdit
} from "../IO/actions";
import ProteinViewer from "./ProteinViewer";
import SequenceViewer from "./SequenceViewer";
import GuideLineup from "./GuideLineup";
import "./style.css";

export interface GeneData {
  domains: Array<any>;
  gene_id: string;
  guides: Array<any>;
  pdbs: Array<any>;
}

interface Domain {
  start: number;
  end: number;
  name: string;
}

interface Props {
  cellline: string;
  geneId: string;
  geneData: GeneData;
  push: (route: string) => {};
  markGeneEdit: (geneId: string) => {};
  toggleGuideSelection: (geneId: string, guideIndex: number) => {};
  setGuideSelection: (geneId: string, guideSelection: number[]) => {};
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
  };

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

  _guidesWithDomains() {
    const { geneData } = this.props;
    return geneData.guides.map((guide: any) => ({
      ...guide,
      domains: geneData.domains
        .filter(
          (domain: Domain) =>
            domain.start < guide.cut_position && domain.end > guide.cut_position
        )
        .map((domain: Domain) => domain.name)
    }));
  }
  _lineupSetGuideSelection = (guideSelection: number[]): void => {
    this.props.setGuideSelection(this.props.geneId, guideSelection);
  }

  render() {
    const { geneData, geneId, cellline } = this.props;
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
            <CelllineSelector />
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
          <GuideLineup
            hoveredGuide={hoveredGuide}
            cellline={cellline}
            setHoveredGuide={this.setHoveredGuide}
            setGuideSelection={this._lineupSetGuideSelection}
            guideClicked={this.guideCheckboxClicked}
            guides={this._guidesWithDomains()}
            className="guideTable"
          />
        </div>
        <div className="containerBottom">
          <SequenceViewer
            cellline={cellline}
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
) => {
  let geneData = state.io.guides.find((v: any) => v.gene_id === geneId);
  return {
    cellline: state.app.cellline,
    geneData: {
      ...geneData,
      guides: geneData.guides.filter(
        (guide: any) => !guide.mutations.includes(state.app.cellline)
      )
    },
    geneId
  };
};

const mapDispatchToProps = (dispatch: any) => ({
  push: (route: string) => dispatch(push(route)),
  toggleGuideSelection: (geneId: string, guideIndex: number) =>
    dispatch(toggleGuideSelection(geneId, guideIndex)),
  setGuideSelection: (geneId: string, guideSelection: number[]) =>
    dispatch(setGuideSelection(geneId, guideSelection)),
  markGeneEdit: (geneId: string) => dispatch(markGeneEdit(geneId))
});

export default connect(mapStateToProps, mapDispatchToProps)(GeneViewer);
