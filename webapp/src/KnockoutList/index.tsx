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
import Table, {
  TableBody,
  TableCell,
  TableHead,
  TableRow
} from "material-ui/Table";
import Paper from "material-ui/Paper";
import "./style.css";

export interface Props {
  guideCount: number;
  setGuideCount: (guideCount: number) => {};
  toggleGuideSelection: (geneId: string, guideIndex: number) => {};
  push: (route: string) => {};
  guides: Array<any>;
}


class KnockoutList extends React.Component<Props, object> {
  componentDidMount() {
    this.updateGuideSelection(this.props.guideCount);
  }

  downloadCSV() {
    const exportFilename = "pavoocExport.csv";

    // TODO orientation->guideOrientation, geneStrand, delete selected, start->startInGene, add exonStart
    const data = [].concat( // flatten array of arrays
      ...this.props.guides.map((gene: any) =>
        gene.guides
          .filter((guide: any) => guide.selected) // only return selected guides
          .map((guide: any) => ({ gene_id: gene.gene_id, ...guide }))
      )
    );

    const columnDelimiter = ",";
    const lineDelimiter = "\n";

    let keys = Object.keys(data[0]);

    let result = "";
    result += keys.join(columnDelimiter);
    result += lineDelimiter;

    data.forEach(function(item: any) {
      let ctr = 0;
      keys.forEach(function(key: string) {
        if (ctr > 0) {
          result += columnDelimiter;
        }

        result += item[key];
        ctr++;
      });
      result += lineDelimiter;
    });
    // now generate a link
    var csvData = new Blob([result], { type: "text/csv;charset=utf-8;" });
    //IE11 & Edge
    if (navigator.msSaveBlob) {
      navigator.msSaveBlob(csvData, exportFilename);
    } else {
      // TODO In FF link must be added to DOM to be clicked
      var link = document.createElement("a");
      link.href = window.URL.createObjectURL(csvData);
      link.setAttribute("download", exportFilename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  }

  updateGuideSelection(guideCount: number) {
    const { guides } = this.props;
    // select all top-guides where no editing has occured before
    for (let gene of guides) {
      // Make sure we don't erase selection edits by the user
      if (gene.edited) {
        continue;
      }
      const sortedGuides = gene.guides.map((guide: any, index: number) => [
        guide,
        index
      ]);
      sortedGuides.sort(function(a: [any, number], b: [any, number]) {
        return b[0].score - a[0].score;
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
    const geneLink = `/geneviewer/${geneGuides.gene_id}`;

    return (
      <TableRow key={geneGuides.gene_id}>
        <TableCell>
          <Link className="tableLink" to={geneLink}>
            {geneGuides.gene_symbol}
          </Link>
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
      <div className="App">
        <div className="AppHeader">
          <h1>PAVOOC</h1>
        </div>
        <div className="AppBody">
          <div className="container">
            <div className="headControl">
              <h2 style={{ flex: 6 }}>Guide recommendations</h2>
              <Button raised={true} style={{ flex: 1, margin: 10 }} onClick={() => this.downloadCSV()}>
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
    guides: state.io.guides.map((gene: any) => {
      let filteredGuides = gene.guides.filter((guide: any) => guide.mutations.includes(state.knockoutList.cellline));
      return {...gene, guides: filteredGuides, filterCount: gene.guides.length - filteredGuides.length};
    })
  };
}

const mapDispatchToProps = (dispatch: any, ownProps: any) => ({
  push: (route: string) => dispatch(push(route)),
  setGuideCount: (guideCount: number) => dispatch(setGuideCount(guideCount)),
  toggleGuideSelection: (geneId: string, guideIndex: number) =>
    dispatch(toggleGuideSelection(geneId, guideIndex))
});

export default connect(mapStateToProps, mapDispatchToProps)(KnockoutList);
