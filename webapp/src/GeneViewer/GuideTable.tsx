import * as React from "react";
import Table, {
  TableBody,
  TableCell,
  TableHead,
  TableRow
} from "material-ui/Table";
import Paper from "material-ui/Paper";

interface State {}

interface Props {
  guides: Array<any>;
}

export default class GuideTable extends React.Component<Props, State> {
  renderTableRow(geneGuides: any) {
    return (
        <TableRow
          key={geneGuides.gene_id}
        >
          <TableCell>
            {geneGuides.gene_id}
          </TableCell>
          <TableCell style={{ whiteSpace: "normal", wordWrap: "break-word" }}>
            Helloooo
          </TableCell>
        </TableRow>
    );
  }
  renderTable() {
    const { guides } = this.props;
    return (
      <Paper>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Gene</TableCell>
              <TableCell>Guides</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {guides.map((geneGuides: any) => this.renderTableRow(geneGuides))}
          </TableBody>
        </Table>
      </Paper>
    );
  }
  render() {
    return this.renderTable();

  }
}
