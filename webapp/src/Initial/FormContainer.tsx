import InitialForm from './Form';
import { push } from "react-router-redux";
import { fetchKnockouts, initialLoad } from '../IO/actions';
import { showMessage } from '../Messages/actions';
// import * as actions from '../actions/';
import { connect } from 'react-redux';

export function mapStateToProps(state: any) {
  return {
    genes: state.io.genes,
  }
}

export function mapDispatchToProps(dispatch: any, ownProps: any) {
  return {
    goKnockout: (geneIds: Array<string>) => {
      dispatch(fetchKnockouts(geneIds));
    },
    goEdit: (geneId: string) => {
      dispatch(push(`/edit/${geneId}`));
    },
    initialLoad: () => dispatch(initialLoad()),
    onMessage: (message: string) => dispatch(showMessage(message)),
    className: ownProps.className
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(InitialForm);

