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
}

export default class GuideTable extends React.Component<Props, State> {
  renderTableRow(guide: any) {
    return (
      <TableRow key={guide.target}>
        <TableCell padding="checkbox">
          <Checkbox checked={false} />
        </TableCell>
        <TableCell style={{ whiteSpace: "normal", wordWrap: "break-word" }}>
          {guide.target}
        </TableCell>
        <TableCell>{guide.score}</TableCell>
      </TableRow>
    );
  }
  renderTable() {
    const { guides, className } = this.props;
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
            {guides.map((guide: any) => this.renderTableRow(guide))}
          </TableBody>
        </Table>
      </Paper>
    );
  }
  render() {
    return this.renderTable();
  }
}
