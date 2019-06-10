import InitialForm from './Form';
import { fetchKnockouts, initialLoad } from '../IO/actions';
import { showMessage } from '../Messages/actions';
import { setGuideCount } from "../IO/actions";
import { setGenome } from "../App/actions";
// import * as actions from '../actions/';
import { connect } from 'react-redux';

export function mapStateToProps(state: any) {
  return {
    guideCount: state.io.guideCount,
    genome: state.app.genome,
    genes: state.io.genes.get(state.app.genome) || new Map<string, string>(),
    cellline: state.app.cellline,
    isFetching: state.io.isFetching
  }
}

export function mapDispatchToProps(dispatch: any, ownProps: any) {
  return {
    setGuideCount: (guideCount: number) => dispatch(setGuideCount(guideCount)),
    setGenome: (genome: string) => dispatch(setGenome(genome)),
    goKnockout: (geneIds: Array<string>, genome:string) => {
      dispatch(fetchKnockouts(geneIds, false, genome));
    },
    goEdit: (geneId: string, genome: string) => {
      dispatch(fetchKnockouts([geneId], true, genome));
    },
    initialLoad: () => dispatch(initialLoad()),
    onMessage: (message: string) => dispatch(showMessage(message)),
    className: ownProps.className,
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(InitialForm);

