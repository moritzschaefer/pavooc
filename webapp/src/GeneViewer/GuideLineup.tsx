import * as React from "react";
import "./style.css";
import "lineupjs/build/LineUpJS.min.css";
import * as LineUpJS from "lineupjs";

interface Guide {
  target: string;
  selected: boolean;
  scores: any;
  domains: Array<string>;
}

interface State {
  lineup: any;
}

interface Props {
  className: string;
  cellline: string;
  guides: Array<Guide>;
  hoveredGuide: number | undefined;
  setHoveredGuide: (hoveredGuide: number | undefined) => void;
  guideClicked: (guideIndex: number) => void;
  setGuideSelection: (guideSelection: number[]) => void;
}

function eqSet(as: Set<number>, bs: Set<number>) {
  if (as.size !== bs.size) {
    return false;
  }
  let equal = true;
  as.forEach((v: number) => {
    if (!bs.has(v)) {
      equal = false;
    }
  });
  return equal;
}

let viewport: HTMLElement | undefined = undefined;

export default class GuideLineup extends React.Component<Props, State> {
  componentDidMount() {
    const lineup = LineUpJS.builder(this._tableArray())
      .sidePanel(false, false)
      .deriveColumns()
      .deriveColors()
      .build(viewport as HTMLElement);
    this._updateSelection(lineup);

    lineup.data.on("selectionChanged", (selection: number[]) => {
      this.props.setGuideSelection(selection);
    });
    this.setState({ lineup });
  }

  _tableArray() {
    // return [0, 5, 10, 15, 20].map((start: number) => (
    //   <p
    //     key={target + start.toString()}
    //     style={{ marginTop: 0.2, marginBottom: 0.2 }}
    //   >
    //     {target.slice(start, start + 5)}
    //   </p>
    // ));
    // sort, retaining indices
    // const sortedGuides = guides.map((guide: Guide, index: number) => [
    //   guide,
    //   index
    // ]);
    // sortedGuides.sort(function(a: [Guide, number], b: [Guide, number]) {
    //   return b[0].scores.azimuth - a[0].scores.azimuth;
    // });
    return this.props.guides.map((guide: Guide, index: number) => ({
      //Label: guide.target,
      d: `Guide ${index}`,
      ...guide.scores
    }));
  }

  shouldComponentUpdate(nextProps: Props, nextState: State) {
    // TODO check if the two arrays differ
    if (nextProps.cellline !== this.props.cellline) {
      console.log("guides might have changed in GuideLineup");
      return true;
    }
    return false;
  }

  componentDidUpdate(prevProps: Props, prevState: State) {
    this._updateSelection(this.state.lineup);
  }

  _updateSelection(lineup: any) {
    // only update if not already the same
    let newSelection = this.props.guides
      .map((guide: Guide, index: number) => [guide, index])
      .filter(([guide, index]: [Guide, number]) => guide.selected)
      .map(([guide, index]: [Guide, number]) => index);

    if (!eqSet(new Set(lineup.data.getSelection()), new Set(newSelection))) {
      lineup.data.setSelection(newSelection);
    }
  }
  // renderTableRow(guide: Guide, index: number) {
  //   const { setHoveredGuide, hoveredGuide } = this.props;
  //   return (
  //     <TableRow
  //       onMouseEnter={() => setHoveredGuide(index)}
  //       onMouseLeave={() => setHoveredGuide(undefined)}
  //       selected={hoveredGuide === index}
  //       key={guide.target}
  //     >
  //       <TableCell padding="checkbox">
  //         <Checkbox
  //           checked={guide.selected}
  //           onChange={() => this.props.guideClicked(index)}
  //         />
  //       </TableCell>
  //       <TableCell
  //         style={{ maxWidth: 60, whiteSpace: "normal", wordWrap: "break-word" }}
  //       >
  //         {this._renderTarget(guide.target)}
  //       </TableCell>
  //       <TableCell>{guide.domains.join()}</TableCell>
  //       <TableCell>{guide.scores.azimuth.toFixed(3)}</TableCell>
  //     </TableRow>
  //   );
  // }

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
