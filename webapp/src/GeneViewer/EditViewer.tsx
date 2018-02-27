// TODO incorporate cellline data
import * as React from "react";
import { connect } from "react-redux";
import { push } from "react-router-redux";

import Button from "material-ui/Button";
import CelllineSelector from "../util/CelllineSelector";
import PdbSelectionDialog from "./PdbSelectionDialog";

import { showMessage } from "../Messages/actions";
import { setEditSelection, markGeneEdit, fetchEdit } from "../IO/actions";
import ProteinViewer from "./ProteinViewer";
import SequenceViewer from "./SequenceViewer";
import GuideLineup from "./GuideLineup";
// import GuideTable from "./GuideTable";
import { downloadCSV } from "../util/functions";
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
  geneCns: boolean;
  bedUrl: string;
  strand: string;
  sequence: string;
  push: (route: string) => {};
  markGeneEdit: (geneId: string) => {};
  setEditSelection: (beforeNotAfter: boolean, guideSelection: number[]) => {};
  fetchEdit: (geneId: string, editPosition: number, padding: number) => {};
  guidesBefore: Array<any>;
  guidesAfter: Array<any>;
  pdbs: Array<any>;
  exons: Array<any>;
  onMessage: (message: string) => {};
  isFetching: boolean;
}

interface State {
  template: string;
  editPosition: number;
  selectedPdb: number;
  hoveredGuide: number | undefined;
  pdbSelectionOpened: boolean;
  padding: number; // how far to look for guides
}

class EditViewer extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      template: "",
      selectedPdb: 0,
      hoveredGuide: undefined,
      pdbSelectionOpened: false,
      editPosition: -1,
      padding: 100
    };
  }

  _setAaEditPosition = (aa: number) => {
    const { exons, strand } = this.props;
    let nucleotides = aa * 3;
    for (let exon of exons) {
      let length = exon.end - exon.start;
      if (nucleotides < length) {
        if (strand === "+") {
          this._setEditPosition(nucleotides + exon.start);
        } else {
          this._setEditPosition(exon.end - nucleotides - 1);
        }
        return;
      } else {
        nucleotides -= length;
      }
    }
  };

  _setEditPosition = (editPosition: number) => {
    const { geneId } = this.props;
    const { padding } = this.state;
    this.setState({ editPosition });
    this.props.fetchEdit(geneId, editPosition, padding);
  };

  setHoveredGuide = (hoveredGuide: number | undefined): void => {
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

  _findAA() {
    // count the amino acids until to the editPosition
    const { exons, sequence, strand } = this.props;
    const { padding, editPosition } = this.state;
    let relativePosition = 0;
    let codon = "";
    // let lastExonEnd = 0;
    // let codonPosition = [];
    for (let exon of exons) {
      if (
        (strand === "+" && exon.end <= editPosition) ||
        (strand === "-" && exon.start > editPosition)
      ) {
        relativePosition += exon.end - exon.start;
        // lastExonEnd = exon.end;
      } else if (
        (strand === "+" && exon.start <= editPosition) ||
        (strand === "-" && exon.end > editPosition)
      ) {
        let inExonPosition;
        if (strand === "+") {
          // inside the cutting exon
          inExonPosition = editPosition - exon.start;
        } else {
          inExonPosition = exon.end - editPosition;
        }
        relativePosition += inExonPosition;
        let offset = relativePosition % 3;
        let codonStart = relativePosition - offset;
        // check if its at the beginning of an exon
        if (exon.start - codonStart < 3 || codonStart + 2 >= exon.end) {
          this.props.onMessage(
            "The codon to edit lies within two exons so I cant show its amino acid"
          );
        } else {
          codon = sequence.slice(padding - offset, padding - offset + 3);
        }
        return { aaPosition: codonStart / 3, codon };
      }
    }
    // cutting exon was never reached
    return { aaPosition: undefined, codon: "" };
  }

  _renderMainContainer() {
    const { cellline, guidesBefore, guidesAfter } = this.props;
    const { hoveredGuide } = this.state;

    return (
      <div className="containerCenter">
        <div className="centerLeft">
          {this._renderProteinViewer()}
          {this._renderSequenceViewer()}
        </div>
        <div className="centerRight">
          <GuideLineup
            hoveredGuide={hoveredGuide}
            cellline={cellline}
            setHoveredGuide={this.setHoveredGuide}
            setGuideSelection={(guideSelection: number[]) =>
              this.props.setEditSelection(true, guideSelection)}
            guides={guidesBefore}
            className="guideTable"
          />
          <GuideLineup
            hoveredGuide={
              typeof hoveredGuide !== "undefined" &&
              hoveredGuide >= guidesBefore.length
                ? hoveredGuide - guidesBefore.length
                : undefined
            }
            cellline={cellline}
            setHoveredGuide={(_hoveredGuide: number) =>
              typeof _hoveredGuide === "undefined"
                ? this.setHoveredGuide(undefined)
                : this.setHoveredGuide(_hoveredGuide + guidesBefore.length)}
            setGuideSelection={(guideSelection: number[]) =>
              this.props.setEditSelection(false, guideSelection)}
            guides={guidesAfter}
            className="guideTable"
          />
        </div>
      </div>
    );
  }

  _renderPreviewContainer() {
    return (
      <div className="previewContainer">
        {this._renderProteinViewer()}
        {this._renderSequenceViewer()}
      </div>
    );
  }

  _renderProteinViewer() {
    const { pdbs } = this.props;
    const { selectedPdb } = this.state;
    let highlightPositions = [];
    try {
      const { aaPosition } = this._findAA();
      if (aaPosition) {
        highlightPositions.push({
          aa_cut_position: aaPosition,
          selected: true
        });
      }
    } catch (e) {
      highlightPositions = []; // TODO set highlight here
    }
    return (
      <ProteinViewer
        className="proteinViewer"
        highlightPositions={highlightPositions}
        aaClicked={this._setAaEditPosition}
        pdb={pdbs[selectedPdb]}
      />
    );
  }

  _renderSequenceViewer() {
    const {
      geneStart,
      geneEnd,
      cellline,
      guidesBefore,
      guidesAfter,
      bedUrl,
      pdbs,
      chromosome,
      exons,
      isFetching
    } = this.props;
    const { selectedPdb, hoveredGuide, editPosition } = this.state;

    const allGuides = guidesBefore ? guidesBefore.concat(guidesAfter) : [];
    const pdb = pdbs[selectedPdb] && pdbs[selectedPdb].pdb;
    return (
      <div style={{ position: "relative" }}>
        {isFetching ? (
          <div className="busyOverlay">
            <div className="spinner" />
          </div>
        ) : null}
        <SequenceViewer
          cellline={cellline}
          editPosition={editPosition}
          editPositionChanged={this._setEditPosition}
          hoveredGuide={hoveredGuide}
          guidesUrl={bedUrl}
          guides={allGuides}
          onGuideHovered={this.setHoveredGuide}
          pdb={pdb}
          onPdbClicked={this._openPdbSelection}
          chromosome={chromosome}
          geneStart={geneStart}
          geneEnd={geneEnd}
          exons={exons}
        />
      </div>
    );
  }

  _csvData() {
    const { geneId, geneCns, guidesBefore, guidesAfter } = this.props;
    const allGuides = guidesBefore ? guidesBefore.concat(guidesAfter) : [];

    // TODO exon_id and aa_cut_position are not included
    return [
      {
        guides: allGuides.map((g: any) => ({
          selected: g.selected,
          otCount: g.otCount,
          start: g.start,
          orientation: g.orientation,
          cut_position: g.cut_position,
          scores: g.scores
        })),
        gene_id: geneId,
        cns: geneCns
      }
    ];
  }

  render() {
    const { geneId, pdbs, sequence, guidesBefore, guidesAfter } = this.props;
    const { pdbSelectionOpened, template } = this.state;
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
            <Button
              raised={true}
              disabled={
                guidesBefore.reduce(
                  (accumulator, currentValue) =>
                    accumulator && !currentValue.selected,
                  true
                ) ||
                guidesAfter.reduce(
                  (accumulator, currentValue) =>
                    accumulator && !currentValue.selected,
                  true
                )
              }
              onClick={() =>
                downloadCSV(this._csvData(), "pavoocEdit.csv", template)}
            >
              &darr; CSV
            </Button>
          </div>
        </div>
        {sequence
          ? this._renderMainContainer()
          : this._renderPreviewContainer()}
      </div>
    );
  }
}

const mapStateToProps = (state: any) => {
  let gene = state.io.detailsData;
  return {
    ...state.io.editData, // guides{Before,After)}, sequence, pdbs
    isFetching: state.io.isFetching,
    cellline: state.app.cellline,
    strand: gene.strand,
    geneStart: gene.start,
    geneEnd: gene.end,
    geneId: gene.gene_id,
    geneCns: gene.cns.includes(state.app.cellline),
    chromosome: gene.chromosome,
    exons: gene.exons,
    // pdbs: state.io.editData.pdbs || []
    pdbs: gene.pdbs || []
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
  setEditSelection: (beforeNotAfter: boolean, guideSelection: number[]) =>
    dispatch(setEditSelection(beforeNotAfter, guideSelection)),
  markGeneEdit: (geneId: string) => dispatch(markGeneEdit(geneId)),
  onMessage: (message: string) => dispatch(showMessage(message))
});

export default connect(mapStateToProps, mapDispatchToProps)(EditViewer);
