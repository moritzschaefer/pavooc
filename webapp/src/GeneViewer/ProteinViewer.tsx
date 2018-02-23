import * as React from "react";
import * as NGL from "ngl";
import RepresentationComponent from "ngl/src/component/representation-component.js";
import StructureRepresentation from "ngl/src/representation/structure-representation.js";
import * as elementResizeEvent from "element-resize-event";

interface State {
  stage: typeof NGL.Stage | undefined;
  representation: typeof RepresentationComponent | undefined;
  hovered: undefined | number;
}

interface Props {
  className: string;
  pdb: any;
  hoveredGuide?: number | undefined;
  setHoveredGuide?: (hoveredGuide: number | undefined) => void;
  highlightPositions: Array<{ aa_cut_position: number; selected: boolean }>;
}

let viewport: HTMLDivElement | undefined = undefined; // TODO try with state again..

// TODO check for chain...
export default class ProteinViewer extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hovered: undefined,
      stage: undefined,
      representation: undefined
    };
  }

  generateScheme() {
    let thisB = this;
    let scheme = NGL.ColormakerRegistry.addScheme(function(
      this: any,
      params: any
    ) {
      this.atomColor = (atom: any) => {
        // the residue index is zero-based, same order as in the loaded file
        const { hoveredGuide, highlightPositions, pdb } = thisB.props;
        const { hovered } = thisB.state;
        let { resno, chainid, chainname } = atom;
        if (chainid !== chainname) {
          console.log(`chainid is not chainname!: ${chainid} !== ${chainname}`);
        }
        if (chainid !== pdb.chain) {
          return 0x505050;
        }
        if (typeof hoveredGuide !== "undefined") {
          try {
            if (
              highlightPositions[hoveredGuide].aa_cut_position ===
              pdb.mappings[resno]
            ) {
              if (highlightPositions[hoveredGuide].selected) {
                return 0xffff00;
              } else {
                return 0xff0000;
              }
            } else {
              return 0x77A7A7;
            }
          } catch (e) {
            console.log(
              "ProteinViewer highlightPositions[hoveredGuide] is undefined!!"
            );
            console.log(hoveredGuide);
            console.log(highlightPositions.length);
            console.log(highlightPositions[hoveredGuide]);
            return 0x0000ff;
          }
        }
        if (hovered && resno === hovered) {
          return 0xF9F9F9;
        }
        // TODO Map<aa_cut_position-pdb.start, guide> for fast lookup
        const guide = highlightPositions.find(
          (g: any) => g.aa_cut_position === pdb.mappings[resno]
        );
        if (guide) {
          if (guide.selected) {
            return 0xbbbb00;
          } else {
            return 0x990000;
          }
        } else {
          return 0x99B9B9;
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
        this.props.highlightPositions.forEach((guide: any, index: number) => {
          if (
            prevProps.highlightPositions[index].selected !== guide.selected ||
            prevProps.highlightPositions[index].aa_cut_position !==
              guide.aa_cut_position
          ) {
            selectionChanged = true;
            return;
          }
        });
      } catch (e) {
        // if guides changed for example
        selectionChanged = true;
      }
      if (
        this.props.pdb &&
        (prevProps.pdb.pdb !== this.props.pdb.pdb ||
          (prevState.stage !== this.state.stage && this.state.stage))
      ) {
        this.loadPdb();
      } else if (
        this.state.representation &&
        (prevProps.hoveredGuide !== this.props.hoveredGuide || selectionChanged ||
        prevState.hovered !== this.state.hovered)
      ) {
        this.state.representation.setColor(this.generateScheme());
        // this.state.representation.update({color: true})
      }
    } else {
      console.log("Error: Stage is not loaded...");
    }
  }

  componentDidMount() {
    // set up ngl
    const stage = new NGL.Stage(viewport);
    stage.setParameters({ backgroundColor: "white" });
    // listen to `hovered` signal to move tooltip around and change its text
    stage.signals.hovered.add((pickingProxy: any) => {
      const { setHoveredGuide, highlightPositions, pdb } = this.props;
      if (pickingProxy && (pickingProxy.atom || pickingProxy.bond)) {
        let { resno, chainid } = pickingProxy.atom;
        if (chainid !== pdb.chain) {
          return;
        }
        const guideIndex = highlightPositions.findIndex(
          (guide: any) => pdb.mappings[resno] === guide.aa_cut_position
        );
        if (setHoveredGuide) {
          if (guideIndex >= 0) {
            setHoveredGuide(guideIndex);
          } else {
            setHoveredGuide(undefined);
          }
        }
        this.setState({ hovered: resno });
      } else {
        if (setHoveredGuide) {
          setHoveredGuide(undefined);
        }
        this.setState({ hovered: undefined });
      }
      // Mouse left hovering area or hovers a non-guide atom
    });

    elementResizeEvent(viewport, () => {
      stage.handleResize();
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
