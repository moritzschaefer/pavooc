// TODO incorporate cellline data
import * as React from "react";
import { connect } from "react-redux";
import { push } from "react-router-redux";

import Button from "material-ui/Button";
import CelllineSelector from "../util/CelllineSelector";
import PdbSelectionDialog from "./PdbSelectionDialog";

import {
  toggleGuideSelection,
  setGuideSelection,
  markGeneEdit,
  fetchEdit
} from "../IO/actions";
import ProteinViewer from "./ProteinViewer";
import SequenceViewer from "./SequenceViewer";
import GuideLineup from "./GuideLineup";
// import GuideTable from "./GuideTable";
import "./style.css";

export interface Exon {
  start: number;
  end: number;
  exon_id: string;
}

interface Props {
  cellline: string;
  geneId: string;
  chromosome: string;
  geneStart: number;
  geneEnd: number;
  sequence: string;
  push: (route: string) => {};
  markGeneEdit: (geneId: string) => {};
  toggleGuideSelection: (geneId: string, guideIndex: number) => {};
  setGuideSelection: (geneId: string, guideSelection: number[]) => {};
  fetchEdit: (geneId: string, editPosition: number, padding: number) => {};
  guidesBefore: Array<any>;
  guidesAfter: Array<any>;
  pdbs: Array<any>;
  canonicalExons: Array<any>;
}

interface State {
  editPosition: number;
  selectedPdb: number;
  hoveredGuide: number | undefined;
  pdbSelectionOpened: boolean;
  padding: 400; // how far to look for guides
}

class EditViewer extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      selectedPdb: 0,
      hoveredGuide: undefined,
      pdbSelectionOpened: false,
      editPosition: -1,
      padding: 400
    };
  }

  _setEditPosition = (editPosition: number) => {
    const { geneId } = this.props;
    const { padding } = this.state;
    this.setState({ editPosition });
    this.props.fetchEdit(geneId, editPosition, padding);
  };

  guideCheckboxClicked = (guideIndex: number) => {
    const { geneId } = this.props;
    this.props.toggleGuideSelection(geneId, guideIndex);
    this.props.markGeneEdit(geneId);
  };

  setHoveredGuide = (hoveredGuide: number): void => {
    this.setState({ hoveredGuide });
  };

  _openPdbSelection = (): void => {
    this.setState({ pdbSelectionOpened: true });
  };

  _selectPdb = (index: number): void => {
    // TODO show selection dialog
    if (index >= 0) {
      this.setState({ selectedPdb: index, pdbSelectionOpened: false });
    } else {
      this.setState({ pdbSelectionOpened: false });
    }
  };

  _lineupSetGuideSelection = (guideSelection: number[]): void => {
    this.props.setGuideSelection(this.props.geneId, guideSelection);
  };

  _findAA(nucletidePosition: number) {
    const { canonicalExons } = this.props;
    let relativePosition = 0;
    let lastExonEnd = 0;
    let codonPosition = [];
    for (let exon of canonicalExons) {
      if (exon.end < nucletidePosition) {
        relativePosition += exon.end - exon.start;
        lastExonEnd = exon.end;
      } else if (exon.start <= nucletidePosition) {
        // inside the cutting exon
        let inExonPosition = nucletidePosition - exon.start;
        relativePosition += inExonPosition;
        let offset = relativePosition % 3;

        let codonStart = relativePosition - offset;
        // check if its at the beginning of an exon
        if (exon.start - codonStart === 1) {
          // need to take some from last Exon
          codonPosition = [lastExonEnd - 1, exon.start, exon.start + 1];
        } else if (exon.start - codonStart === 2) {
          codonPosition = [lastExonEnd - 2, lastExonEnd - 1, exon.start];
        } else {
          // normal case
          codonPosition = [codonStart, codonStart + 1, codonStart + 2];
        }
        // TODO shit! what if codonStart + 1 > exon.end???
        return codonPosition;
      }
    }
    // cutting exon was never reached
    return undefined;
  }
  _renderMainContainer() {
    const {
      cellline,
      guidesBefore,
      guidesAfter,
      pdbs,
    } = this.props;
    const { selectedPdb, hoveredGuide } = this.state;
    return (
      <div className="containerCenter">
        <div className="centerLeft">
          <ProteinViewer
            hoveredGuide={hoveredGuide}
            setHoveredGuide={this.setHoveredGuide}
            className="proteinViewer"
            guides={guidesBefore.concat(guidesAfter)}
            pdb={pdbs[selectedPdb]}
          />
          {this._renderSequenceViewer()}
        </div>
        <div className="centerRight">
          <GuideLineup
            hoveredGuide={hoveredGuide}
            cellline={cellline}
            setHoveredGuide={this.setHoveredGuide}
            setGuideSelection={this._lineupSetGuideSelection}
            guideClicked={this.guideCheckboxClicked}
            guides={guidesBefore}
            className="guideTable"
          />
          <GuideLineup
            hoveredGuide={hoveredGuide}
            cellline={cellline}
            setHoveredGuide={this.setHoveredGuide}
            setGuideSelection={this._lineupSetGuideSelection}
            guideClicked={this.guideCheckboxClicked}
            guides={guidesAfter}
            className="guideTable"
          />
        </div>
      </div>
    );
  }

  _renderSequenceViewer() {
    const {
      geneStart,
      geneEnd,
      cellline,
      guidesBefore,
      guidesAfter,
      pdbs,
      chromosome,
      canonicalExons
    } = this.props;
    const { selectedPdb, hoveredGuide, editPosition } = this.state;

    const allGuides = guidesBefore ? guidesBefore.concat(guidesAfter) : [];
    const pdb = pdbs[selectedPdb] && pdbs[selectedPdb].pdb;
    return (
      <SequenceViewer
        cellline={cellline}
        editPosition={editPosition}
        editPositionChanged={this._setEditPosition}
        hoveredGuide={hoveredGuide}
        guides={allGuides}
        onGuideHovered={this.setHoveredGuide}
        pdb={pdb}
        onPdbClicked={this._openPdbSelection}
        chromosome={chromosome}
        geneStart={geneStart}
        geneEnd={geneEnd}
        exons={canonicalExons}
      />
    );
  }

  render() {
    // TODO: in the beginning show the sequenceviewer only. after guide loading show the rest (pdb and guideslist)
    const {
      geneId,
      pdbs,
      sequence
    } = this.props;
    const { pdbSelectionOpened } = this.state;
    return (
      <div className="mainContainer">
        <PdbSelectionDialog
          data={pdbs.map((pdb: any) => pdb.pdb)}
          opened={pdbSelectionOpened}
          selectIndex={this._selectPdb}
        />
        <div className="containerTop">
          <div className="geneViewerHeader">
            <Button
              onClick={() => this.props.push("/")}
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
        {sequence ? this._renderMainContainer() : this._renderSequenceViewer()}
      </div>
    );
  }
}

const mapStateToProps = (
  state: any,
  { match: { params: { geneId } } }: { match: { params: { geneId: string } } }
) => {
  let gene = (state.io.genes.get && state.io.genes.get(geneId)) || {};
  return {
    ...state.io.editData, // guides{Before,After)}, sequence, pdbs
    cellline: state.app.cellline,
    geneStart: gene.start,
    geneEnd: gene.end,
    geneId,
    canonicalExons: state.io.editData.canonicalExons,
    chromosome: gene.chromosome,
    pdbs: state.io.editData.pdbs || []
    // geneData: {
    //   ...geneData,
    //   guides: geneData.guides.filter(
    //     (guide: any) => !guide.mutations.includes(state.app.cellline)
    //   )
    // },
  };
};

const mapDispatchToProps = (dispatch: any) => ({
  fetchEdit: (geneId: string, editPosition: number, padding: number) =>
    dispatch(fetchEdit(geneId, editPosition, padding)),
  push: (route: string) => dispatch(push(route)),
  toggleGuideSelection: (geneId: string, guideIndex: number) =>
    dispatch(toggleGuideSelection(geneId, guideIndex)),
  setGuideSelection: (geneId: string, guideSelection: number[]) =>
    dispatch(setGuideSelection(geneId, guideSelection)),
  markGeneEdit: (geneId: string) => dispatch(markGeneEdit(geneId))
});

export default connect(mapStateToProps, mapDispatchToProps)(EditViewer);
