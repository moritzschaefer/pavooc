import * as React from "react";
import "./style.css";
import "lineupjsx/build/LineUpJSx.css";
import {
  LineUp,
  LineUpStringColumnDesc,
  LineUpNumberColumnDesc,
  LineUpCategoricalColumnDesc,
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
  mutations: Array<string>;
  start: number;
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

export default class GuideLineup extends React.Component<Props, State> {

  _tableArray() {
    return this.props.guides.map((guide: Guide, index: number) => ({
      d: `Guide ${index}`,
      domain: guide.domains ? guide.domains.join(",") : "",
      affected: guide.mutations.includes(this.props.cellline) ? "yes" : "no",
      start: guide.start,
      ...{...guide.scores,
        Doench2016CFDScore: 1 - guide.scores.Doench2016CFDScore
      }
    }));
  }

  shouldComponentUpdate(nextProps: Props, nextState: State) {
    //    return false;
    // if (nextProps.setGuideSelection !== this.props.setGuideSelection) {
    //   console.log("setGuideSelection did change");
    //   return true;
    // }
    //
    // if (nextProps.setHoveredGuide !== this.props.setHoveredGuide) {
    //   console.log("setHoveredGuide did change");
    //   return true;
    // }

    if (
      nextProps.cellline !== this.props.cellline ||
      nextProps.hoveredGuide !== this.props.hoveredGuide
    ) {
      console.log("guides might have changed in GuideLineup");
      return true;
    }
    let changed = false;
    nextProps.guides.forEach((guide: Guide, index: number) => {
      // comparing target and selected should be enough
      if (
        !this.props.guides[index] ||
        this.props.guides[index].target !== guide.target ||
        this.props.guides[index].selected !== guide.selected
      ) {
        changed = true;
        return;
      }
    });
    return changed;
  }

  _selectionIndices() {
    let newSelection = this.props.guides
      .map((guide: Guide, index: number) => [guide, index])
      .filter(([guide, index]: [Guide, number]) => guide.selected)
      .map(([guide, index]: [Guide, number]) => index);
    return newSelection;
  }
  _onSelectionChanged = (selection: number[]) => this.props.setGuideSelection(selection);
  _onHighlightChanged = (highlight: number) =>
            this.props.setHoveredGuide(
              highlight === -1 ? undefined : highlight
            );


  guideMutationExists(): boolean  {
    const { guides, cellline } = this.props;
    return guides.some((guide: any) => guide.mutations.includes(cellline));
  }

  render() {
    return (
      <div className={this.props.className}>
        <LineUp
          data={this._tableArray()}
          defaultRanking={false}
          onSelectionChanged={this._onSelectionChanged}
          onHighlightChanged={this._onHighlightChanged}
          selection={this._selectionIndices()}
          highlight={this.props.hoveredGuide}
          sidePanel={false}
        >
          <LineUpStringColumnDesc column="d" label="Label" width={70} />
          <LineUpCategoricalColumnDesc column="domain" label="Domain" width={90} />
          {/* <LineUpStringColumnDesc column="start" label="Position" width={70} /> */}
          <LineUpCategoricalColumnDesc
            label="SNV affected"
            column="affected"
            color="orange"
            width={70}
          />
          <LineUpNumberColumnDesc
            label="On target 1"
            column="pavooc"
            domain={[0, 1]}
            color="green"
          />
          <LineUpNumberColumnDesc
            label="On target 2"
            column="azimuth"
            domain={[0, 1]}
            color="blue"
          />
          <LineUpNumberColumnDesc
            label="Off target (inverted)"
            column="Doench2016CFDScore"
            domain={[0, 1]}
            color="red"
          />

          <LineUpRanking sortBy="Scores:desc">
            <LineUpSupportColumn type="selection" />
            <LineUpColumn column="d" />
            <LineUpColumn column="domain" />
            <LineUpWeightedSumColumn label="Scores">
              <LineUpWeightedColumn column="pavooc" weight={0.5} />
              <LineUpWeightedColumn column="azimuth" weight={0.1} />
              <LineUpWeightedColumn column="Doench2016CFDScore" weight={0.4} />
            </LineUpWeightedSumColumn>
            {/* <LineUpColumn column="start" /> */}
            { this.guideMutationExists() ?
              <LineUpColumn column="affected"/> : null
            }

          </LineUpRanking>
        </LineUp>
      </div>
    );
  }
}
