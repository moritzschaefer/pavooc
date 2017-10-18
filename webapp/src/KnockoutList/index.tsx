import * as React from 'react';
import { push } from 'react-router-redux';
import { connect } from 'react-redux';
import Button from 'material-ui/Button';
import Table, { TableBody, TableCell, TableHead, TableRow } from 'material-ui/Table';
import Paper from 'material-ui/Paper';

export interface Props {
  push: any;
  guides: any;
}


class KnockoutList extends React.Component<Props, object> {
  renderTableRow(geneGuides: any) {
    const scores = geneGuides.guides.map((v: any) => v.score);

    return (
      <TableRow key={geneGuides.gene_id}>
        <TableCell>{geneGuides.gene_id}</TableCell>
        <TableCell style={{ whiteSpace: 'normal', wordWrap: 'break-word' }}>{scores.join(', ')}</TableCell>
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
      <div>
        { this.renderTable() }
        <Button onClick={() => this.props.push('/')}>Back</Button>
      </div>
    );
  }
}

const mapStateToProps = (state: any) => ({
  guides: state.io.guides,
});

const mapDispatchToProps = (dispatch: any, ownProps: any) => ({
  push: (route: any) => dispatch(push(route))
});

export default connect(
  mapStateToProps,
  mapDispatchToProps)(KnockoutList);
