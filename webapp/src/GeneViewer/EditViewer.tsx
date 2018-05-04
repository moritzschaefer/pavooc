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

import { showMessage } from "../Messages/actions";
import { setGuideSelection, markGeneEdit } from "../IO/actions";
import ProteinViewer from "./ProteinViewer";
import SequenceViewer, { SeqEditData } from "./SequenceViewer";
import GuideLineup from "./GuideLineup";
// import GuideTable from "./GuideTable";
import { downloadCSV, guidesWithDomains, arraysEqual } from "../util/functions";
import "./style.css";

export interface Exon {
  start: number;
  end: number;
  exon_id: string;
}

interface Props {
  geneData: any;
  cellline: string;
  geneId: string;
  geneSymbol: string;
  chromosome: string;
  geneCns: boolean;
  strand: string;
  sequence: string;
  push: (route: string) => {};
  markGeneEdit: (geneId: string) => {};
  setGuideSelection: (geneId: string, guideSelection: number[]) => void;
  guides: Array<any>;
  pdbs: Array<any>;
  exons: Array<any>;
  onMessage: (message: string) => {};
  isFetching: boolean;
  padding: number; // how far to look for guides
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
        cutDistance: 0,
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

  _cutEditSequence() {
    const { guides, sequence, exons, padding } = this.props;
    const guide = guides.find((guide: any) => guide.selected);
    if (!guide) {
      return "";
    }
    const start = guide.cut_position - padding;
    const end = guide.cut_position + padding;

    const geneStart = Math.min(...exons.map((exon: any) => exon.start));
    const geneEnd = Math.max(...exons.map((exon: any) => exon.end));

    const editedSequence = sequence.slice(
      Math.max(start - geneStart, 0),
      Math.min(end - geneStart, geneEnd - geneStart)
    );
    return editedSequence;
  }
  componentDidMount() {
    this.setState({ editedSequence: this._cutEditSequence() });
  }

  componentDidUpdate(prevProps: Props, prevState: State) {
    const { guides, sequence } = this.props;
    if (
      prevProps.sequence !== sequence ||
      !arraysEqual(
        guides.map((guide: any) => guide.selected),
        prevProps.guides.map((guide: any) => guide.selected)
      )
    ) {
      // reset editedSequence!
      this.setState({ editedSequence: this._cutEditSequence() });
    }
  }

  _onGuideClicked = (index: number): void => {
    const { geneId } = this.props;
    this.props.setGuideSelection(geneId, [index]);
  };

  _pdbAaClicked = (aa: number) => {
    const { strand, guides, geneId } = this.props;
    // if there are no guides, fetch guides
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
      var index = guides.findIndex(
        (guide: any) => guide.aa_cut_position === aa
      );
      if (index >= 0) {
        this.props.setGuideSelection(geneId, [index]);
      }
    }
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

  _renderMainContainer() {
    const { cellline, geneId, geneData } = this.props;
    const { hoveredGuide } = this.state;

    // TODO guideSelection should only return ONE selection
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
              this.props.setGuideSelection(geneId, guideSelection)}
            guides={guidesWithDomains(geneData)}
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
    const { pdbs, guides, padding, strand } = this.props;
    const { selectedPdb, editedSequence } = this.state;
    let highlightPositions: Array<{
      aa_cut_position: number;
      selected: boolean;
    }> = [];

    const seqEditData = this._editRange();
    if (seqEditData && typeof seqEditData.aaStart !== "undefined") {
      let originalSequence = this._cutEditSequence();
      for (var i = 0, len = seqEditData.sequence.length / 3; i < len; i++) {
        // TODO enable selected, if this one has been edited
        const sequenceStart = this._editPosition() - padding;
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
          originalSequence.slice(inSeqPosition, inSeqPosition + 3) !==
          editedSequence.slice(inSeqPosition, inSeqPosition + 3);
        highlightPositions.push({
          aa_cut_position: seqEditData.aaStart + i,
          selected
        });
      }
    } else {
      // show guide cut positions
      highlightPositions = guides.map((guide: any) => ({
        aa_cut_position: guide.aa_cut_position,
        selected: guide.selected
      }));
    }

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
      cellline,
      guides,
      pdbs,
      chromosome,
      exons,
      isFetching
    } = this.props;
    const { selectedPdb, hoveredGuide } = this.state;

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
          onGuideClicked={this._onGuideClicked}
          hoveredGuide={hoveredGuide}
          guides={guides}
          onGuideHovered={this.setHoveredGuide}
          pdb={pdb}
          onPdbClicked={this._openPdbSelection}
          chromosome={chromosome}
          geneStart={Math.min(...exons.map((exon: any) => exon.start))}
          geneEnd={Math.max(...exons.map((exon: any) => exon.end))}
          exons={exons}
        />
      </div>
    );
  }

  _csvData() {
    const { geneId, geneCns, guides, chromosome } = this.props;

    // TODO exon_id and aa_cut_position are not included
    return [
      {
        guides: guides.map((g: any) => ({
          selected: g.selected,
          target: g.target,
          otCount: g.otCount,
          start: g.start,
          orientation: g.orientation,
          cut_position: g.cut_position,
          aa_cut_position: g.aa_cut_position,
          scores: g.scores,
          exon_id: g.exon_id
        })),
        gene_id: geneId,
        chromosome,
        cns: geneCns
      }
    ];
  }

  _setEditedCodon = (position: number, codon: string) => {
    const { padding } = this.props;
    let { editedSequence } = this.state;
    const sequenceStart = this._editPosition() - padding;
    const inSequencePosition = position - sequenceStart;

    this.setState({
      editedSequence:
        editedSequence.slice(0, inSequencePosition) +
        codon +
        editedSequence.slice(inSequencePosition + 3, editedSequence.length)
    });
  };

  _editedCodon = () => {
    const { padding } = this.props;
    const editCodonPosition = this.state.codonEditProps.position;
    const { editedSequence } = this.state;
    if (!editedSequence) {
      return "";
    }

    const sequenceStart = this._editPosition() - padding;
    const inSequencePosition = editCodonPosition - sequenceStart;
    const editedCodon = editedSequence.slice(
      inSequencePosition,
      inSequencePosition + 3
    );
    return editedCodon;
  };

  _onEditCodonClicked = (editCodonPosition: number) => {
    // get sequence:
    const { padding, strand } = this.props;

    const sequenceStart = this._editPosition() - padding;
    const inSequencePosition = editCodonPosition - sequenceStart;
    const originalCodon = this._cutEditSequence().slice(
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
        cutDistance: Math.abs(editCodonPosition - this._editPosition()),
        originalCodon
      }
    });
  };
  _editPosition(): number {
    // Only call if selected
    const { guides } = this.props;
    const guide = guides.find((guide: any) => guide.selected);
    return guide.cut_position;
  }

  _editRange(): SeqEditData | undefined {
    // returns left and right IN-FRAME cut positions if left and right
    // guides are selected or undefined
    const { editedSequence } = this.state;
    const { strand, guides, padding } = this.props;
    if (
      !editedSequence ||
      !guides ||
      !guides.find((guide: any) => guide.selected)
    ) {
      return undefined;
    }

    let guide = guides.find((guide: any) => guide.selected);
    let start = guide.cut_position - padding;
    let end = guide.cut_position + padding;

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
        const localStart = start - (this._editPosition() - padding);

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

  _onCSVClick = () => {
    const { editedSequence } = this.state;
    const { padding, guides } = this.props;
    const guide = guides.find((guide: any) => guide.selected);
    if (!guide) {
      return;
    }
    const templateStart = guide.cut_position - padding;
    let originalSequence = this._cutEditSequence();

    const editPositions = [];
    for (var i = 0, len = originalSequence.length; i < len; i++) {
      if (originalSequence[i] !== editedSequence[i]) {
        editPositions.push(i);
      }
    }

    downloadCSV(this._csvData(), "pavoocEdit.csv", {
      template: editedSequence,
      templateStart,
      originalSequence,
      editPositions
    });
  };

  _renderTopContainer() {
    const { selectedPdb } = this.state;
    const { geneSymbol, pdbs, strand } = this.props;

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
          {geneSymbol}&nbsp; Strand: {strand} PDB:{" "}

          <a href="#" onClick={this._openPdbSelection}>
            {pdbs[selectedPdb] ? pdbs[selectedPdb].pdb : ""}
          </a>
        </h2>
        <div className="topControls">
          <CelllineSelector />
          <Button
            raised={true}
            disabled={!this._editRange()}
            onClick={this._onCSVClick}
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
  let geneData = state.io.knockoutData[0];
  return {
    sequence: geneData.sequence,
    padding: state.app.padding,
    isFetching: state.io.isFetching,
    cellline: state.app.cellline,
    geneData: geneData,
    guides: geneData.guides,
    strand: geneData.strand,
    geneSymbol: geneData.gene_symbol,
    geneId: geneData.gene_id,
    geneCns: geneData.cns.includes(state.app.cellline),
    chromosome: geneData.chromosome,
    exons: geneData.exons,
    // pdbs: state.io.editData.pdbs || []
    pdbs: geneData.pdbs || []
    // geneData: {
    //   ...geneData,
    //   guides: geneData.guides.filter(
    //     (guide: any) => !guide.mutations.includes(state.app.cellline)
    //   )
    // },
  };
};

const mapDispatchToProps = (dispatch: any) => ({
  push: (route: string) => dispatch(push(route)),
  setGuideSelection: (geneId: string, guideSelection: number[]) =>
    dispatch(setGuideSelection(geneId, guideSelection)),
  markGeneEdit: (geneId: string) => dispatch(markGeneEdit(geneId)),
  onMessage: (message: string) => dispatch(showMessage(message))
});

export default connect(mapStateToProps, mapDispatchToProps)(EditViewer);
