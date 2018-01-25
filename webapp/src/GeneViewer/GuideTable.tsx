import * as React from "react";
import Table, {
  TableBody,
  TableCell,
  TableHead,
  TableRow
} from "material-ui/Table";
import Checkbox from "material-ui/Checkbox";
import Paper from "material-ui/Paper";
import "./style.css";

interface Guide {
  target: string;
  selected: boolean;
  scores: any;
  domains: Array<string>;
}

interface State {}

interface Props {
  className: string;
  guides: Array<Guide>;
  hoveredGuide: number | undefined;
  setHoveredGuide: (hoveredGuide: number | undefined) => void;
  guideClicked: (guideIndex: number) => void;
}

export default class GuideTable extends React.Component<Props, State> {
  _renderTarget(target: string) {
    return [0, 5, 10, 15, 20].map((start: number) => (
            <p
              key={target + start.toString()}
              style={{ marginTop: 0.2, marginBottom: 0.2 }}
            >
              {target.slice(start, start + 5)}
            </p>
          ))
  }

  renderTableRow(guide: Guide, index: number) {
    const { setHoveredGuide, hoveredGuide } = this.props;
    return (
      <TableRow
        onMouseEnter={() => setHoveredGuide(index)}
        onMouseLeave={() => setHoveredGuide(undefined)}
        selected={hoveredGuide === index}
        key={guide.target}>
        <TableCell padding="checkbox">
          <Checkbox checked={guide.selected} onChange={() => this.props.guideClicked(index)} />
        </TableCell>
        <TableCell
          style={{ maxWidth: 60, whiteSpace: "normal", wordWrap: "break-word" }}
        >
          {this._renderTarget(guide.target)}
        </TableCell>
        <TableCell>{guide.domains.join()}</TableCell>
        <TableCell>{guide.scores.azimuth.toFixed(3)}</TableCell>
      </TableRow>
    );
  }

  renderTable() {
    const { guides, className } = this.props;
    // sort, retaining indices
    const sortedGuides = guides.map((guide: Guide, index: number) => [guide, index])
    sortedGuides.sort(function(a: [Guide, number], b: [Guide, number]) {
      return b[0].scores.aziumth - a[0].scores.azimuth;
    });

    return (
      <Paper className={className}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Use</TableCell>
              <TableCell>Guide</TableCell>
              <TableCell>Domains</TableCell>
              <TableCell>Score</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedGuides.map(([guide, index]: [Guide, number]) => this.renderTableRow(guide, index))}
          </TableBody>
        </Table>
      </Paper>
    );
  }

  render() {
    return this.renderTable();
  }
}
