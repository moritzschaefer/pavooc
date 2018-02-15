import * as React from "react";
import "./style.css";
import "lineupjsx/build/LineUpJSx.css";
import {
  LineUp,
  LineUpStringColumnDesc,
  LineUpNumberColumnDesc,
  LineUpRanking,
  LineUpColumn,
  LineUpWeightedSumColumn,
  LineUpWeightedColumn,
  LineUpSupportColumn
} from "lineupjsx";

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
  showDomain?: boolean;
}

// function eqSet(as: Set<number>, bs: Set<number>) {
//   if (as.size !== bs.size) {
//     return false;
//   }
//   let equal = true;
//   as.forEach((v: number) => {
//     if (!bs.has(v)) {
//       equal = false;
//     }
//   });
//   return equal;
// }
//

export default class GuideLineup extends React.Component<Props, State> {
  _tableArray() {
    // TODO fix as Array needs conversion <- ??
    return (this.props.guides as Array<
      Guide
    >).map((guide: Guide, index: number) => ({
      d: `Guide ${index}`,
      Domain: guide.domains ? guide.domains.join(",") : "",
      ...guide.scores
    }));
  }

  shouldComponentUpdate(nextProps: Props, nextState: State) {
    //TODO check if the two arrays differ

    // if (nextProps.cellline !== this.props.cellline) {
    //   console.log("guides might have changed in GuideLineup");
    //   return true;
    // }
    return false;
  }

  _selectionIndices() {
    // only update if not already the same
    let newSelection = (this.props.guides as Array<Guide>)
      .map((guide: Guide, index: number) => [guide, index])
      .filter(([guide, index]: [Guide, number]) => guide.selected)
      .map(([guide, index]: [Guide, number]) => index);
    console.log(newSelection);
    return newSelection;
  }

  render() {
    return (
      <div className={this.props.className}>
        <LineUp
          data={this._tableArray()}
          defaultRanking={false}
          onSelectionChanged={(selection: number[]) =>
            this.props.setGuideSelection(selection)}
          onHighlightChanged={(highlight: number) =>
            this.props.setHoveredGuide(
              highlight === -1 ? undefined : highlight
            )}
          selection={this._selectionIndices()}
          highlight={this.props.hoveredGuide}
          sidePanel={false}
        >
          <LineUpStringColumnDesc column="d" label="Label" width={80} />
          <LineUpStringColumnDesc column="Domain" label="Domain" width={60} />
          <LineUpNumberColumnDesc
            column="azimuth"
            domain={[0, 1]}
            color="red"
          />
          <LineUpNumberColumnDesc
            column="Doench2016CDFScore"
            domain={[0, 1]}
            color="green"
          />
          <LineUpNumberColumnDesc
            column="Hsu2013"
            domain={[0, 100]}
            color="blue"
          />

          <LineUpRanking sortBy="Scores:desc">
            <LineUpSupportColumn type="selection" />
            <LineUpColumn column="d" />
            <LineUpColumn column="Domain" />
            <LineUpWeightedSumColumn label="Scores">
              <LineUpWeightedColumn column="azimuth" weight={0.45} />
              <LineUpWeightedColumn column="Doench2016CDFScore" weight={0.35} />
              <LineUpWeightedColumn column="Hsu2013" weight={0.2} />
            </LineUpWeightedSumColumn>
          </LineUpRanking>
        </LineUp>
      </div>
    );
  }
}
