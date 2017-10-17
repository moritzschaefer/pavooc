import InitialForm from './Form';
import { fetchKnockouts } from '../IO/actions';
//import * as actions from '../actions/';
import { connect } from 'react-redux';
// import { push } from 'react-router-redux';

export function mapStateToProps() {
  return {
    geneIds: ['ENSG00000251357.4.guides', 'ENSG10000251357.4.guides', 'ENSG00000251352.4.guides', 'ENSG04000251357.4.guides', 'ENSG00a000251357.4.guides', 'ENSG0e0000251357.4.guides'],
    celllines: ['A', 'B', 'CCC', 'AC']
  }
}

export function mapDispatchToProps(dispatch: any, ownProps: any) {
  return {
    go: (geneIds: Array<string>, cellline: string) => dispatch(fetchKnockouts(geneIds, cellline))
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(InitialForm);
