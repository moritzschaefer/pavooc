import InitialForm from './Form';
import { fetchKnockouts, initialLoad } from '../IO/actions';
import { showMessage } from '../Messages/actions';
import { setGuideCount } from "../IO/actions";
// import * as actions from '../actions/';
import { connect } from 'react-redux';

export function mapStateToProps(state: any) {
  return {
    guideCount: state.io.guideCount,
    genes: state.io.genes,
    cellline: state.app.cellline,
    isFetching: state.io.isFetching
  }
}

export function mapDispatchToProps(dispatch: any, ownProps: any) {
  return {
    setGuideCount: (guideCount: number) => dispatch(setGuideCount(guideCount)),
    goKnockout: (geneIds: Array<string>) => {
      dispatch(fetchKnockouts(geneIds, false));
    },
    goEdit: (geneId: string) => {
      dispatch(fetchKnockouts([geneId], true));
    },
    initialLoad: () => dispatch(initialLoad()),
    onMessage: (message: string) => dispatch(showMessage(message)),
    className: ownProps.className,
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(InitialForm);

