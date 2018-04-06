import * as React from "react";
import { push } from "react-router-redux";
import { Link } from "react-router-dom";
import { connect } from "react-redux";
import Button from "material-ui/Button";
import Select from "material-ui/Select";
import Input, { InputLabel } from "material-ui/Input";
import { MenuItem } from "material-ui/Menu";
import { setGuideCount } from "./actions";
import { toggleGuideSelection } from "../IO/actions";
import { FormControl } from "material-ui/Form";
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
  guideCount: number;
  setGuideCount: (guideCount: number) => {};
  toggleGuideSelection: (geneId: string, guideIndex: number) => {};
  push: (route: string) => {};
  knockoutData: Array<any>;
}

class KnockoutList extends React.Component<Props, object> {
  componentDidMount() {
    this.updateGuideSelection(this.props.guideCount);
  }


  updateGuideSelection(guideCount: number) {
    const { knockoutData } = this.props;
    // select all top-guides where no editing has occured before
    for (let gene of knockoutData) {
      // Make sure we don't erase selection edits by the user
      if (gene.edited) {
        continue;
      }

      const sortedGuides = guidesWithDomains(gene).map((guide: any, index: number) => [
        guide,
        index
      ]);
      sortedGuides.sort(function(a: [any, number], b: [any, number]) {
        // domain gives a bonus of 0.1
        let bScore =  (b[0].scores.azimuth * 0.6 + b[0].scores.Doench2016CFDScore * 0.4);
        if (b[0].domains.length > 0) {
          bScore += 0.1;
        }
        let aScore = (a[0].scores.azimuth * 0.6 + a[0].scores.Doench2016CFDScore * 0.4);
        if (a[0].domains.length > 0) {
          aScore += 0.1;
        }
        return bScore - aScore;
      });
      // enable first <guideCount> guides
      for (let [guide, index] of sortedGuides.slice(0, guideCount)) {
        if (!guide.selected) {
          this.props.toggleGuideSelection(gene.gene_id, index);
        }
      }
      // disable the guides after <guideCount>
      for (let [guide, index] of sortedGuides.slice(guideCount)) {
        if (guide.selected) {
          this.props.toggleGuideSelection(gene.gene_id, index);
        }
      }
    }

    this.props.setGuideCount(guideCount);
  }

  renderGuideCountSelector() {
    const { guideCount } = this.props;
    return (
      <FormControl style={{ flex: 2 }}>
        <InputLabel htmlFor="guides-count">Guides per gene</InputLabel>
        <Select
          value={guideCount}
          onChange={event =>
            this.updateGuideSelection(parseInt(event.target.value, 10))}
          input={<Input id="guides-count" />}
          MenuProps={{
            PaperProps: {
              style: {
                maxHeight: 200
              }
            }
          }}
        >
          {Array.from(new Array(10), (_: {}, i: number) => (
            <MenuItem value={i} key={i}>
              {i}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    );
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
              This gene is affected by a copy number segmentation in the
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
                onClick={() => downloadCSV(this.props.knockoutData, "pavoocKnockout.csv")}
              >
                &darr; CSV
              </Button>
              {this.renderGuideCountSelector()}
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
    guideCount: state.knockoutList.guideCount,
    knockoutData: state.io.knockoutData.map((gene: any) => {
      let filteredGuides = gene.guides.filter(
        (guide: any) => !guide.mutations.includes(state.app.cellline)
      );
      return {
        ...gene,
        cns: gene.cns.includes(state.app.cellline),
        guides: filteredGuides,
        filterCount: gene.guides.length - filteredGuides.length
      };
    })
  };
};

const mapDispatchToProps = (dispatch: any, ownProps: any) => ({
  push: (route: string) => dispatch(push(route)),
  setGuideCount: (guideCount: number) => dispatch(setGuideCount(guideCount)),
  toggleGuideSelection: (geneId: string, guideIndex: number) =>
    dispatch(toggleGuideSelection(geneId, guideIndex))
});

export default connect(mapStateToProps, mapDispatchToProps)(KnockoutList);
