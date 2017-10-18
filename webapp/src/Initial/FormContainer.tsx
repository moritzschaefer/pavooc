import InitialForm from './Form';
import { fetchKnockouts, initialLoad } from '../IO/actions';
//import * as actions from '../actions/';
import { connect } from 'react-redux';
// import { push } from 'react-router-redux';

export function mapStateToProps(state: any) {
  return {
    geneIds: state.io.geneIds,
    celllines: state.io.celllines
  }
}

export function mapDispatchToProps(dispatch: any, ownProps: any) {
  return {
    go: (geneIds: Array<string>, cellline: string) => dispatch(fetchKnockouts(geneIds, cellline)),
    initialLoad: () => dispatch(initialLoad())
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(InitialForm);
