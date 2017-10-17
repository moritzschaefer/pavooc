import InitialForm from '../components/InitialForm';
//import * as actions from '../actions/';
import { StoreState } from '../types/index';
import { connect, Dispatch } from 'react-redux';
// import { push } from 'react-router-redux';

export function mapStateToProps({}: StoreState) {
  return {
    geneIds: ['ENSG00000251357.4.guides', 'ENSG10000251357.4.guides', 'ENSG00000251352.4.guides', 'ENSG04000251357.4.guides', 'ENSG00a000251357.4.guides', 'ENSG0e0000251357.4.guides'],
    celllines: ['A', 'B', 'CCC', 'AC']
  }
}

export function mapDispatchToProps(dispatcher: Dispatch<'bac'>) {
  return {
    //go: dispatcher(push('/knockout'))
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(InitialForm);
