import * as React from "react";
import { push } from "react-router-redux";
import { Link } from "react-router-dom";
import { connect } from "react-redux";
import Button from "material-ui/Button";
import Table, {
  TableBody,
  TableCell,
  TableHead,
  TableRow
} from "material-ui/Table";
import Paper from "material-ui/Paper";
import "./style.css";

export interface Props {
  push: (route: string) => {};
  guides: Array<any>;
}

class KnockoutList extends React.Component<Props, object> {
  renderTableRow(geneGuides: any) {
    const scores = geneGuides.guides.map((v: any) => v.score);
    const geneLink = `/geneviewer/${geneGuides.gene_id}`;

    return (
        <TableRow
          key={geneGuides.gene_id}
        >
          <TableCell>
            <Link className="tableLink" to={geneLink}>
              {geneGuides.gene_id}
            </Link>
          </TableCell>
          <TableCell style={{ whiteSpace: "normal", wordWrap: "break-word" }}>
            <Link className="tableLink" to={geneLink}>
              {scores.join(", ")}
            </Link>
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
    return (
      <div className="container">
        <h2>Guide recommendations</h2>
        {this.renderTable()}
        <Button onClick={() => this.props.push("/")}>Back</Button>
      </div>
    );
  }
}

const mapStateToProps = (state: any) => ({
  guides: state.io.guides.slice(0, state.geneViewer.guideCount)
});

const mapDispatchToProps = (dispatch: any, ownProps: any) => ({
  push: (route: string) => dispatch(push(route))
});

export default connect(mapStateToProps, mapDispatchToProps)(KnockoutList);
