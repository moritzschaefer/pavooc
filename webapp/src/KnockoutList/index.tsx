import * as React from "react";
import { push } from "react-router-redux";
import { Link } from "react-router-dom";
import { connect } from "react-redux";
import Button from "material-ui/Button";
import { toggleGuideSelection } from "../IO/actions";
import CelllineSelector from "../util/CelllineSelector";
import Table, {
  TableBody,
  TableCell,
  TableHead,
  TableRow
} from "material-ui/Table";
import Paper from "material-ui/Paper";
import "./style.css";
import { downloadCSV, guidesWithDomains } from "../util/functions";

export interface Props {
  toggleGuideSelection: (geneId: string, guideIndex: number) => {};
  push: (route: string) => {};
  knockoutData: Array<any>;
  cellline: string;
}

class KnockoutList extends React.Component<Props, object> {
  componentDidMount() {
  }

  renderTableRow(geneGuides: any) {
    const targets = geneGuides.guides
      .filter((guide: any) => guide.selected)
      .map((v: any) => v.target);
    const { filterCount, cns } = geneGuides;
    const geneLink = `/geneviewer/${geneGuides.gene_id}`;

    return (
      <TableRow key={geneGuides.gene_id}>
        <TableCell>
          <Link className="tableLink" to={geneLink}>
            {geneGuides.gene_symbol}
          </Link>
          {filterCount > 0 ? (
            <div style={{ color: "orange" }}>
              {filterCount} guides filtered due to cellline mutations
            </div>
          ) : null}
          {cns ? (
            <div style={{ color: "orange" }}>
              This gene is affected by a copy number alteration in the
              selected cellline
            </div>
          ) : null}
        </TableCell>
        <TableCell
          style={{
            whiteSpace: "normal",
            wordWrap: "break-word",
            fontFamily: "Courier"
          }}
        >
          <Link className="tableLink" to={geneLink}>
            {targets.join(", ")}
          </Link>
        </TableCell>
      </TableRow>
    );
  }
  renderTable() {
    const { knockoutData } = this.props;
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
            {knockoutData.map((geneGuides: any) =>
              this.renderTableRow(geneGuides)
            )}
          </TableBody>
        </Table>
      </Paper>
    );
  }
  render() {
    return (
      <div className="App">
        <div className="AppHeader">
          <h1>PAVOOC</h1>
        </div>
        <div className="AppBody">
          <div className="container">
            <div className="headControl">
              <h2 style={{ flex: 6 }}>Guide recommendations</h2>
              <CelllineSelector />
              <Button
                raised={true}
                style={{ flex: 1, margin: 10 }}
                onClick={() =>
                  downloadCSV(
                    this.props.knockoutData.map((geneData: any) => ({
                      ...geneData,
                      guides: guidesWithDomains(geneData)
                    })),
                    "pavoocKnockout.csv"
                  )}
              >
                &darr; CSV
              </Button>
            </div>
            {this.renderTable()}
            <Button onClick={() => this.props.push("/")}>Back</Button>
          </div>
        </div>
      </div>
    );
  }
}

const mapStateToProps = (state: any) => {
  // Filter guides for mutations within the selected cellline
  return {
    cellline: state.app.cellline,
    knockoutData: state.io.knockoutData.map((gene: any) => {
      let filteredGuides = gene.guides.filter(
        (guide: any) => !guide.mutations.includes(state.app.cellline)
      );
      return {
        ...gene,
        cns: gene.cns.includes(state.app.cellline),
        filterCount: gene.guides.length - filteredGuides.length
      };
    })
  };
};

const mapDispatchToProps = (dispatch: any, ownProps: any) => ({
  push: (route: string) => dispatch(push(route)),
  toggleGuideSelection: (geneId: string, guideIndex: number) =>
    dispatch(toggleGuideSelection(geneId, guideIndex, false))
});

export default connect(mapStateToProps, mapDispatchToProps)(KnockoutList);
