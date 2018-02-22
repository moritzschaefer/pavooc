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
  guides: Array<Guide>;
  hoveredGuide: number | undefined;
  setHoveredGuide: (hoveredGuide: number | undefined) => void;
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
    return this.props.guides.map((guide: Guide, index: number) => ({
      d: `Guide ${index}`,
      Domain: guide.domains ? guide.domains.join(",") : "",
      ...guide.scores
    }));
  }

  shouldComponentUpdate(nextProps: Props, nextState: State) {
    return false;
    // if (nextProps.setGuideSelection !== this.props.setGuideSelection) {
    //   console.log("setGuideSelection did change");
    //   return true;
    // }
    //
    // if (nextProps.setHoveredGuide !== this.props.setHoveredGuide) {
    //   console.log("setHoveredGuide did change");
    //   return true;
    // }
    //
    // if (
    //   nextProps.cellline !== this.props.cellline ||
    //   nextProps.hoveredGuide !== this.props.hoveredGuide
    // ) {
    //   console.log("guides might have changed in GuideLineup");
    //   return true;
    // }
    // let changed = false;
    // nextProps.guides.forEach((guide: Guide, index: number) => {
    //   // comparing target and selected should be enough
    //   if (
    //     !this.props.guides[index] ||
    //     this.props.guides[index].target !== guide.target ||
    //     this.props.guides[index].selected !== guide.selected
    //   ) {
    //     changed = true;
    //     return;
    //   }
    // });
    // return changed;
  }

  _selectionIndices() {
    let newSelection = this.props.guides
      .map((guide: Guide, index: number) => [guide, index])
      .filter(([guide, index]: [Guide, number]) => guide.selected)
      .map(([guide, index]: [Guide, number]) => index);
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
            column="Doench2016CFDScore"
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
              <LineUpWeightedColumn column="Doench2016CFDScore" weight={0.35} />
              <LineUpWeightedColumn column="Hsu2013" weight={0.2} />
            </LineUpWeightedSumColumn>
          </LineUpRanking>
        </LineUp>
      </div>
    );
  }
}
