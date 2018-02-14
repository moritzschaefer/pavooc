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
  guides: Array<Guide> | Map<number, Guide>;
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
      .column(LineUpJS.buildNumberColumn("azimuth", [0, 1]))
      .column(LineUpJS.buildNumberColumn("Doench2016CDFScore", [0, 1]))
      .column(LineUpJS.buildNumberColumn("Hsu2013", [0, 100]))
      .column(LineUpJS.buildStringColumn("d"))
      .column(LineUpJS.buildStringColumn("Domain"))
      .ranking(
        LineUpJS.buildRanking()
          .selection()
          .column("d")
          .column("Domain")
          .weightedSum(
            "azimuth",
            0.45,
            "Doench2016CDFScore",
            0.45,
            "Hsu2013",
            0.1
          )
          .sortBy("score")
      )
      .deriveColors()
      .build(viewport as HTMLElement);
    this._updateSelection(lineup);

    lineup.data.on("selectionChanged", (selection: number[]) => {
      this.props.setGuideSelection(selection);
    });
    this.setState({ lineup });
  }

  // _guidesMap() {
  //
  // }

  _tableArray() {
    // TODO fix as Array needs conversion
    return (this.props.guides as Array<Guide>).map((guide: Guide, index: number) => ({
      d: `Guide ${index}`,
      Domain: guide.domains.join(","),
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
    this.state.lineup.data.setData(this._tableArray());
    this._updateSelection(this.state.lineup);
  }

  _updateSelection(lineup: any) {
    // only update if not already the same
    let newSelection = (this.props.guides as Array<Guide>)
      .map((guide: Guide, index: number) => [guide, index])
      .filter(([guide, index]: [Guide, number]) => guide.selected)
      .map(([guide, index]: [Guide, number]) => index);

    if (!eqSet(new Set(lineup.data.getSelection()), new Set(newSelection))) {
      lineup.data.setSelection(newSelection);
    }
  }

  render() {
    return (
      <div className={this.props.className}>
        <div
          ref={(v: HTMLDivElement) => {
            viewport = v;
          }}
          style={{ position: "relative", width: "100%", height: "100%" }}
        />
      </div>
    );
  }
}
