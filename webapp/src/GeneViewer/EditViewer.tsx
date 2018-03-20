// TODO if we change "padding" after gathering data, everything fails! possible solution: gather new
// guides after padding change so everything resets
// TODO incorporate cellline data
import * as React from "react";
import { connect } from "react-redux";
import { push } from "react-router-redux";

import Button from "material-ui/Button";
import CelllineSelector from "../util/CelllineSelector";
import PdbSelectionDialog from "./PdbSelectionDialog";
import CodonEditDialog, { Props as CodonEditProps } from "./CodonEditDialog";

import { setEditPosition /* , setPadding */ } from "../App/actions";
import { showMessage } from "../Messages/actions";
import { setEditSelection, markGeneEdit, fetchEdit } from "../IO/actions";
import ProteinViewer from "./ProteinViewer";
import SequenceViewer, { SeqEditData } from "./SequenceViewer";
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
  geneSymbol: string;
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
  editPosition: number;
  padding: number; // how far to look for guides
  setEditPosition: (editPosition: number) => void;
  setPadding: (padding: number) => void;
}

interface State {
  selectedPdb: number;
  hoveredGuide: number | undefined;
  pdbSelectionOpened: boolean;
  codonEditProps: CodonEditProps;
  editedSequence: string;
}

class EditViewer extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      editedSequence: "",
      selectedPdb: 0,
      hoveredGuide: undefined,
      pdbSelectionOpened: false,
      codonEditProps: {
        strand: "+",
        originalCodon: "",
        editedCodon: "",
        position: -1,
        setEditedCodon: this._setEditedCodon,
        onClose: () =>
          this.setState({
            codonEditProps: {
              ...this.state.codonEditProps,
              opened: false
            }
          }),
        opened: false
      }
    };
  }
  componentDidMount() {
    this.setState({ editedSequence: this.props.sequence });
  }

  componentDidUpdate(prevProps: Props, prevState: State) {
    if (prevProps.sequence !== this.props.sequence) {
      // reset editedSequence!
      this.setState({ editedSequence: this.props.sequence });
    }
  }

  _pdbAaClicked = (aa: number) => {
    const { exons, strand, guidesBefore, guidesAfter } = this.props;
    // if there are no guides, fetch guides
    if (guidesBefore.length === 0) {
      let nucleotides = aa * 3;
      for (let exon of exons) {
        // TODO does this work for reverse as well?
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
    } else {
      const seqEditData = this._editRange();
      // if we clicked in the editable region, edit the selected AA
      if (seqEditData && seqEditData.aaStart) {
        if (
          aa >= seqEditData.aaStart &&
          aa < seqEditData.aaStart + seqEditData.sequence.length / 3
        ) {
          let aaNucleotideOffset = (aa - seqEditData.aaStart) * 3;

          if (strand === "-") {
            aaNucleotideOffset =
              seqEditData.sequence.length - aaNucleotideOffset - 3;
          }
          this._onEditCodonClicked(seqEditData.start + aaNucleotideOffset);
        }
      } else {
        // else, see if we selected a cut position so we can select a guide
        var beforeIndex = guidesBefore.findIndex(
          (guide: any) => guide.aa_cut_position === aa
        );
        if (beforeIndex >= 0) {
          this.props.setEditSelection(true, [beforeIndex]);
        }
        var afterIndex = guidesAfter.findIndex(
          (guide: any) => guide.aa_cut_position === aa
        );
        if (afterIndex >= 0) {
          this.props.setEditSelection(false, [afterIndex]);
        }
      }
    }
  };

  _setEditPosition = (editPosition: number) => {
    const { geneId, padding } = this.props;
    this.props.setEditPosition(editPosition);
    this.props.fetchEdit(geneId, editPosition, padding);
  };

  setHoveredGuide = (hoveredGuide: number | undefined): void => {
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

  _findAA() {
    // count the amino acids until to the editPosition
    const { exons, sequence, strand, padding, editPosition } = this.props;
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
          {this._renderTopContainer()}
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
    const {
      pdbs,
      guidesBefore,
      guidesAfter,
      sequence,
      editPosition,
      padding,
      strand
    } = this.props;
    const { selectedPdb, editedSequence } = this.state;
    let highlightPositions: Array<{
      aa_cut_position: number;
      selected: boolean;
    }> = [];

    const seqEditData = this._editRange();
    if (seqEditData && typeof seqEditData.aaStart !== "undefined") {
      for (var i = 0, len = seqEditData.sequence.length / 3; i < len; i++) {
        // TODO enable selected, if this one has been edited
        const sequenceStart = editPosition - padding;
        let inSeqPosition;
        if (strand === "+") {
          inSeqPosition = seqEditData.start + i * 3 - sequenceStart;
        } else {
          inSeqPosition =
            seqEditData.start +
            (seqEditData.sequence.length - i * 3 - 3) -
            sequenceStart;
        }
        const selected =
          sequence.slice(inSeqPosition, inSeqPosition + 3) !==
          editedSequence.slice(inSeqPosition, inSeqPosition + 3);
        highlightPositions.push({
          aa_cut_position: seqEditData.aaStart + i,
          selected
        });
      }
    } else {
      // show guide cut positions
      highlightPositions = guidesBefore
        .concat(guidesAfter)
        .map((guide: any) => ({
          aa_cut_position: guide.aa_cut_position,
          selected: guide.selected
        }));
    }

    // TODO delete along with _findAA
    // try {
    //   const { aaPosition } = this._findAA();
    //   if (aaPosition) {
    //     highlightPositions.push({
    //       aa_cut_position: aaPosition,
    //       selected: true
    //     });
    //   }
    // } catch (e) {
    //   highlightPositions = []; // TODO set highlight here
    // }
    return (
      <ProteinViewer
        className="proteinViewer"
        highlightPositions={highlightPositions}
        aaClicked={this._pdbAaClicked}
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
      isFetching,
      editPosition
    } = this.props;
    const { selectedPdb, hoveredGuide } = this.state;

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
          editData={this._editRange()}
          onEditCodonClicked={this._onEditCodonClicked}
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
          target: g.target,
          otCount: g.otCount,
          start: g.start,
          orientation: g.orientation,
          cut_position: g.cut_position,
          aa_cut_position: g.aa_cut_position,
          scores: g.scores
        })),
        gene_id: geneId,
        cns: geneCns
      }
    ];
  }

  _setEditedCodon = (position: number, codon: string) => {
    const { editPosition, padding } = this.props;
    let { editedSequence } = this.state;
    const sequenceStart = editPosition - padding;
    const inSequencePosition = position - sequenceStart;

    this.setState({
      editedSequence:
        editedSequence.slice(0, inSequencePosition) +
        codon +
        editedSequence.slice(inSequencePosition + 3, editedSequence.length)
    });
  };

  _editedCodon = () => {
    const { editPosition, padding } = this.props;
    const editCodonPosition = this.state.codonEditProps.position;
    const { editedSequence } = this.state;
    if (!editedSequence) {
      return "";
    }

    const sequenceStart = editPosition - padding;
    const inSequencePosition = editCodonPosition - sequenceStart;
    const editedCodon = editedSequence.slice(
      inSequencePosition,
      inSequencePosition + 3
    );
    return editedCodon;
  };

  _onEditCodonClicked = (editCodonPosition: number) => {
    // get sequence:
    const { sequence, editPosition, padding, strand } = this.props;

    const sequenceStart = editPosition - padding;
    const inSequencePosition = editCodonPosition - sequenceStart;
    const originalCodon = sequence.slice(
      inSequencePosition,
      inSequencePosition + 3
    );

    // calculate editedCodon and originalCodon
    this.setState({
      codonEditProps: {
        ...this.state.codonEditProps,
        strand,
        opened: true,
        position: editCodonPosition,
        originalCodon
      }
    });
  };

  _editRange(): SeqEditData | undefined {
    // returns left and right IN-FRAME cut positions if left and right
    // guides are selected or undefined
    const { editedSequence } = this.state;
    const {
      guidesBefore,
      guidesAfter,
      strand,
      editPosition,
      padding
    } = this.props;
    if (
      !editedSequence ||
      !editPosition ||
      !guidesBefore ||
      editPosition === -1
    ) {
      return undefined;
    }

    let start = Math.max(
      ...guidesBefore
        .filter(guide => guide.selected)
        .map(guide => guide.cut_position)
    );
    let end = Math.min(
      ...guidesAfter
        .filter(guide => guide.selected)
        .map(guide => guide.cut_position)
    );
    if (!Number.isInteger(start) || !Number.isInteger(end)) {
      return undefined;
    }

    let nucleotideCount = 0;
    const exons = this.props.exons.slice();
    if (strand === "-") {
      // -strand exons need to be reversed even though the first (rightmost) exon is first in array
      exons.reverse();
    }
    // we dont have to take care of strand because the frame fits from both sides..
    for (let exon of exons) {
      if (exon.end > start) {
        // if start is outside an exon, set it to start of next exon
        if (start < exon.start) {
          start = exon.start;
        }
        // check for offset, TODO sure we should ADD and not SUBTRACT
        const offset = (nucleotideCount + (start - exon.start)) % 3;
        if (offset === 1) {
          start += 2;
        } else if (offset === 2) {
          start += 1;
        }
        let aaStart = (nucleotideCount + (start - exon.start)) / 3;

        // we only treat one exon so this has to be the same exon for 'end'
        if (end > exon.end) {
          end = exon.end;
        }
        end -= (nucleotideCount + (end - exon.start)) % 3;
        const l = end - start;
        const localStart = start - (editPosition - padding);

        if (strand === "-") {
          let totalNucleotides = exons
            .map((exon: any) => exon.end - exon.start)
            .reduce((a: number, b: number) => a + b, 0);
          aaStart = (totalNucleotides - l) / 3 - aaStart;
        }

        return {
          start,
          aaStart,
          sequence: editedSequence.slice(localStart, localStart + l),
          strand
        };
      } else {
        nucleotideCount += exon.end - exon.start;
      }
    }
    return undefined;
  }

  _renderTopContainer() {
    const { selectedPdb, editedSequence } = this.state;
    const { geneSymbol, pdbs } = this.props;

    return (
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
        <h2 className="heading">
          {geneSymbol}&nbsp; PDB:{" "}
          {pdbs[selectedPdb] ? pdbs[selectedPdb].pdb : ""}
        </h2>
        <div className="topControls">
          <CelllineSelector />
          <Button
            raised={true}
            disabled={!this._editRange()}
            onClick={() =>
              downloadCSV(this._csvData(), "pavoocEdit.csv", editedSequence)}
          >
            &darr; CSV
          </Button>
        </div>
      </div>
    );
  }

  render() {
    const { pdbs } = this.props;
    const { pdbSelectionOpened, codonEditProps } = this.state;
    return (
      <div className="mainContainer">
        <PdbSelectionDialog
          data={pdbs.map((pdb: any) => pdb.pdb)}
          opened={pdbSelectionOpened}
          selectIndex={this._selectPdb}
        />
        <CodonEditDialog
          {...codonEditProps}
          editedCodon={this._editedCodon()}
        />
        {this._renderMainContainer()}
      </div>
    );
  }
}

const mapStateToProps = (state: any) => {
  let gene = state.io.detailsData || {};
  return {
    ...state.io.editData, // guides{Before,After)}, sequence, pdbs
    editPosition: state.app.editPosition,
    padding: state.app.padding,
    isFetching: state.io.isFetching,
    cellline: state.app.cellline,
    strand: gene.strand,
    geneStart: gene.start,
    geneEnd: gene.end,
    geneSymbol: gene.gene_symbol,
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
  setEditPosition: (editPosition: number) =>
    dispatch(setEditPosition(editPosition)),
  onMessage: (message: string) => dispatch(showMessage(message))
});

export default connect(mapStateToProps, mapDispatchToProps)(EditViewer);
