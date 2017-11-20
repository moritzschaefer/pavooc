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

interface State {}

interface Props {
  className: string;
  guides: any;
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

  renderTableRow(guide: any, index: number) {
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
        <TableCell>{guide.score.toFixed(3)}</TableCell>
      </TableRow>
    );
  }

  renderTable() {
    const { guides, className } = this.props;
    // sort, retaining indices
    const sortedGuides = guides.map((guide: any, index: number) => [guide, index])
    sortedGuides.sort(function(a: [any, number], b: [any, number]) {
      return b[0].score - a[0].score;
    });

    return (
      <Paper className={className}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Use</TableCell>
              <TableCell>Guide</TableCell>
              <TableCell>Score</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedGuides.map(([guide, index]: [any, number]) => this.renderTableRow(guide, index))}
          </TableBody>
        </Table>
      </Paper>
    );
  }

  render() {
    return this.renderTable();
  }
}
