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

// TODO check for chain...
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
      // TODO guides[hovered] is undefined sometimes
      let aa_cut_position;
      try {
        aa_cut_position = guides[hoveredGuide].aa_cut_position;
      } catch (e) {
        console.log(`${hoveredGuide} doesnt exist in ProteinViewer`);
        return
      }
      const highlightPosition = aa_cut_position - pdb.start;
      if (aa_cut_position >= 0 && highlightPosition) {
        selection = `${highlightPosition - 1}-${highlightPosition + 2}`; // bugfix extending indices
      }
    } else {
      const cuts = [];
      for (let guide of guides) {
        const inPdbPosition = guide.aa_cut_position - pdb.start;
        if (
          guide.aa_cut_position >= 0 &&
          inPdbPosition >= 0 &&
          inPdbPosition < pdb.end - pdb.start
        ) {
          cuts.push(`${inPdbPosition - 1}-${inPdbPosition + 2}`); // bugfix extending indices
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

  generateScheme() {
    const { hoveredGuide, guides, pdb } = this.props;
    let scheme = NGL.ColormakerRegistry.addScheme(function(
      this: any,
      params: any
    ) {
      this.atomColor = function(atom: any) {
        // the residue index is zero-based, same order as in the loaded file
        let { resno } = atom;
        if (typeof hoveredGuide !== "undefined") {
          try {
            if (guides[hoveredGuide].aa_cut_position === pdb.mappings[resno]) {
              if (guides[hoveredGuide].selected) {
                return 0xffff00;
              } else {
                return 0xff0000;
              }
            } else {
              return 0x777777;
            }
          } catch (e) {
            console.log("ProteinViewer guides[hoveredGuide] is undefined!!");
            console.log(hoveredGuide);
            console.log(guides.length);
            console.log(guides[hoveredGuide]);
            return 0x0000ff;
          }
        }
        // TODO Map<aa_cut_position-pdb.start, guide> for fast lookup
        const guide = guides.find(
          (g: any) => g.aa_cut_position === pdb.mappings[resno]
        );
        if (guide) {
          if (guide.selected) {
            return 0xbbbb00;
          } else {
            return 0x990000;
          }
        } else {
          return 0x999999;
        }
      };
    });
    return scheme;
  }

  loadPdb() {
    const { pdb } = this.props;
    const { stage } = this.state;

    // find and highlight cut positions
    stage.removeAllComponents();
    let scheme = this.generateScheme();

    stage
      .loadFile(`rcsb://${pdb.pdb}`)
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
      let selectionChanged = false;
      try {
        this.props.guides.forEach((guide: any, index: number) => {
          if (prevProps.guides[index].selected !== guide.selected) {
            selectionChanged = true;
            return;
          }
        });
      } catch (e) { // if guides changed for example
        selectionChanged = true;
      }
      if (
        this.props.pdb &&
        ((prevProps.pdb.pdb !== this.props.pdb.pdb) ||
        (prevState.stage !== this.state.stage && this.state.stage))
      ) {
        this.loadPdb();
      } else if (
        this.state.representation &&
        (prevProps.hoveredGuide !== this.props.hoveredGuide || selectionChanged)
      ) {
        this.state.representation.setColor(this.generateScheme());
        // this.state.representation.update({color: true})
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
    stage.signals.hovered.add((pickingProxy: any) => {
      if (pickingProxy && (pickingProxy.atom || pickingProxy.bond)) {
        let { resno } = pickingProxy.atom;
        const guideIndex = guides.findIndex(
          (guide: any) => pdb.mappings[resno] === guide.aa_cut_position
        );
        if (guideIndex >= 0) {
          setHoveredGuide(guideIndex);
        }
      } else {
        // Mouse left hovering area
        setHoveredGuide(undefined);
      }
    });
    this.setState({ stage });
  }

  // TODO render nothing if this.props.pdb is undefined such that guide table can grow
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
