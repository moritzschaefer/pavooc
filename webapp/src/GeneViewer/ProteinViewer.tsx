import * as React from "react";
import * as NGL from "ngl";
import RepresentationComponent from "ngl/src/component/representation-component.js";
import StructureRepresentation from "ngl/src/representation/structure-representation.js";

interface State {
  stage: typeof NGL.Stage | undefined;
  representation: typeof RepresentationComponent | undefined;
}

interface Props {
  className: string;
  pdb: any;
  hoveredGuide: number | undefined;
  setHoveredGuide: (hoveredGuide: number | undefined) => void;
  guides: any;
}

let viewport: HTMLDivElement | undefined = undefined; // TODO try with state again..

export default class ProteinViewer extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      stage: undefined,
      representation: undefined
    };
  }

  updateHovering() {
    // Update the representation/highlighting of NGL
    const { representation } = this.state;
    const { pdb, hoveredGuide, guides } = this.props;

    if (!representation) {
      throw "representation MUST not be undefined";
    }

    // Either show the hoveredGuide, or highlight all guides
    let selection = "not all";
    if (hoveredGuide) {
      const aa_cut_position = guides[hoveredGuide].aa_cut_position;
      const highlightPosition = aa_cut_position - (pdb.SP_BEG);
      if (aa_cut_position >= 0 && highlightPosition ) {
        selection = `${highlightPosition-1}-${highlightPosition + 2}`; // bugfix extending indices
      }
    } else {
      const cuts = [];
      for (let guide of guides) {
        const inPdbPosition = guide.aa_cut_position - (pdb.SP_BEG);
        if (guide.aa_cut_position >= 0 && inPdbPosition >= 0 && inPdbPosition < pdb.SP_END - pdb.SP_BEG) {
          cuts.push(`${inPdbPosition-1}-${inPdbPosition+2}`); // bugfix extending indices
        }
      }
      if (cuts.length === 0) {
        console.log("Zero Guides found. Must not have. TODO: convert to throw");
      } else {
        selection = cuts.join(" or ");
      }
    }
    representation.setSelection(selection);
  }

  loadPdb() {
    const { pdb, guides } = this.props;
    const { stage } = this.state;
    const { props } = this;


    // find and highlight cut positions
    stage.removeAllComponents();

    let scheme = NGL.ColormakerRegistry.addScheme( function(this: any, params: any ) {
      this.atomColor = function( atom: any ) {
        // the residue index is zero-based, same order as in the loaded file
        // TODO cache atom.residue.index (because it is slow!) Map<atom, atom.residue.index>
        let res = atom.residue.index;
        if (props.hoveredGuide) {
          if (guides[props.hoveredGuide].aa_cut_position - pdb.SP_BEG === res) {
            return 0xFFFF00;
          }
        }
        // TODO Map<aa_cut_position-pdb.SP_BEG, guide> for fast lookup
        if (guides.find((guide: any) => guide.aa_cut_position - pdb.SP_BEG === res)) {
          return 0xFF0000;
        }
        return 0x777777;
      };
    } );

    stage
      .loadFile(`rcsb://${pdb.PDB}`)
      .then((structureRepresentation: typeof StructureRepresentation) => {
        let representation: typeof RepresentationComponent = structureRepresentation.addRepresentation(
          "cartoon",
          { color: scheme }
        );
        this.setState({ representation });
        structureRepresentation.autoView();
      });
  }

  componentDidUpdate(prevProps: Props, prevState: State) {
    if (this.state.stage) {
      if (
        prevProps.pdb.PDB !== this.props.pdb.PDB ||
        (prevState.stage !== this.state.stage && this.state.stage)
      ) {
        this.loadPdb();
      } else if (prevProps.hoveredGuide !== this.props.hoveredGuide) {
        this.updateHovering();
      }

      // initial Highlighting
      if (prevState.representation !== this.state.representation) {
        this.updateHovering();
      }
    } else {
      console.log("Error: Stage is not loaded...");
    }
  }

  componentDidMount() {
    const { setHoveredGuide, guides, pdb } = this.props;
    // set up ngl
    const stage = new NGL.Stage(viewport);
    stage.setParameters({ backgroundColor: "black" });
    // listen to `hovered` signal to move tooltip around and change its text
    stage.signals.hovered.add((pickingProxy: any) =>  {
      if (pickingProxy && (pickingProxy.atom || pickingProxy.bond)) {
        // TODO find corresponding guide!!
        // setHoveredGuide(pickingProxy.pid);
        const res = pickingProxy.atom.residue.index;
        // TODO fixme, not the correct position.. (or other positions suck..)
        const guideIndex = guides.findIndex((guide: any) => res === guide.aa_cut_position - pdb.SP_BEG);
        if (guideIndex) {
          setHoveredGuide(guideIndex);
        }
      } else {
        // Mouse left hovering area
        setHoveredGuide(undefined);
      }
    });
    this.setState({ stage });
  }

  render() {
    return (
      <div className={this.props.className}>
        <div
          ref={(v: HTMLDivElement) => {
            viewport = v;
          }}
          style={{ flex: 1 }}
        />
      </div>
    );
  }
}
