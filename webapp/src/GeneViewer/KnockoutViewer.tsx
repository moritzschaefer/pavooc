// TODO we can delete all markGeneEdit stuff
import * as React from "react";
import { connect } from "react-redux";
import { push } from "react-router-redux";

import Button from "material-ui/Button";
import CelllineSelector from "../util/CelllineSelector";
import PdbSelectionDialog from "./PdbSelectionDialog";

import {
  toggleGuideSelection,
  setGuideSelection,
  markGeneEdit
} from "../IO/actions";
import ProteinViewer from "./ProteinViewer";
import SequenceViewer from "./SequenceViewer";
import GuideLineup from "./GuideLineup";
// import GuideTable from "./GuideTable";
import "./style.css";
import { Exon } from "./EditViewer";
import { guidesWithDomains } from "../util/functions";

export interface GeneData {
  domains: Array<any>;
  cns: Array<string>;
  gene_id: string;
  gene_symbol: string;
  guides: Array<any>;
  pdbs: Array<any>;
  exons: Array<Exon>;
  chromosome: string;
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
  pdbSelectionOpened: boolean;
}

class KnockoutViewer extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      selectedPdb: 0,
      hoveredGuide: undefined,
      pdbSelectionOpened: false
    };
  }

  setHoveredGuide = (hoveredGuide: number): void => {
    this.setState({ hoveredGuide });
  };

  _openPdbSelection = (): void => {
    this.setState({ pdbSelectionOpened: true });
  };

  _selectPdb = (index: number | undefined): void => {
    // TODO show selection dialog
    if (typeof index !== "undefined" && index >= 0) {
      this.setState({ selectedPdb: index, pdbSelectionOpened: false });
    } else {
      this.setState({ pdbSelectionOpened: false });
    }
  };

  _aaClicked = (aa: number) => {
    const { geneData, geneId } = this.props;
    const index = geneData.guides.findIndex(
      (guide: any) => guide.aa_cut_position === aa
    );
    if (index >= 0) {
      this.props.toggleGuideSelection(geneId, index); // warning: two guides on one amino acid? only one is selected
    }
  };

  _onGuideClicked = (index: number): void => {
    const { geneId } = this.props;
    this.props.toggleGuideSelection(geneId, index);
  };

  _lineupSetGuideSelection = (guideSelection: number[]): void => {
    this.props.setGuideSelection(this.props.geneId, guideSelection);
  };

  render() {
    const { geneData, cellline } = this.props;
    const { selectedPdb, hoveredGuide, pdbSelectionOpened } = this.state;
    return (
      <div className="mainContainer">
        <PdbSelectionDialog
          data={geneData.pdbs.map((pdb: any) => pdb.pdb)}
          opened={pdbSelectionOpened}
          selectIndex={this._selectPdb}
        />
        <div className="containerTop">
          <Button
            onClick={() => this.props.push("/knockout")}
            raised={true}
            className="backButton"
          >
            Back
          </Button>
          <h2 className="heading">
            {geneData.gene_symbol}&nbsp; PDB:{" "}
            {geneData.pdbs[selectedPdb] ? geneData.pdbs[selectedPdb].pdb : ""}
          </h2>
          <div className="topControls">
            <CelllineSelector />
          </div>
        </div>
        <div className="containerCenter">
          <ProteinViewer
            hoveredPosition={hoveredGuide}
            setHoveredPosition={this.setHoveredGuide}
            aaClicked={this._aaClicked}
            className="proteinViewer"
            highlightPositions={geneData.guides}
            pdb={geneData.pdbs[selectedPdb]}
          />
          <GuideLineup
            hoveredGuide={hoveredGuide}
            cellline={cellline}
            showDomain={true}
            setHoveredGuide={this.setHoveredGuide}
            setGuideSelection={this._lineupSetGuideSelection}
            guides={guidesWithDomains(geneData)}
            className="guideTable"
          />
        </div>
        <div className="containerBottom">
          <SequenceViewer
            cellline={cellline}
            hoveredGuide={hoveredGuide}
            cns={geneData.cns}
            guides={geneData.guides}
            onGuideClicked={this._onGuideClicked}
            onGuideHovered={this.setHoveredGuide}
            pdb={geneData.pdbs[selectedPdb] && geneData.pdbs[selectedPdb].pdb}
            onPdbClicked={this._openPdbSelection}
            chromosome={geneData.chromosome}
            exons={geneData.exons}
            geneStart={Math.min(
              ...geneData.exons.map((exon: any) => exon.start)
            )}
            geneEnd={Math.max(...geneData.exons.map((exon: any) => exon.end))}
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
  let geneData = state.io.knockoutData.find((v: any) => v.gene_id === geneId);
  return {
    cellline: state.app.cellline,
    geneData: {
      ...geneData,
      guides: geneData.guides.filter(
        (guide: any) => !guide.mutations.includes(state.app.cellline) // TODO this filter destroys important indices!!
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

export default connect(mapStateToProps, mapDispatchToProps)(KnockoutViewer);
