import { fetchKnockoutsSuccess, FetchKnockouts }  from './actions';
import { FETCH_KNOCKOUTS, FETCH_KNOCKOUTS_SUCCESS }  from './actionTypes';
import { Observable } from 'rxjs/Observable';
import { combineEpics } from 'redux-observable';
import { push } from 'react-router-redux'

const fetchKnockoutsApi = (geneIds: any, cellline: string) => {
  const request = fetch(`/api/knockout`, {method: 'POST', body: JSON.stringify({gene_ids: geneIds})})
    .then(response => response.json());
  return Observable.from(request);
}

const fetchKnockoutsEpic = (action$: any) =>
  action$.ofType(FETCH_KNOCKOUTS)
    .mergeMap((action: FetchKnockouts) =>
      fetchKnockoutsApi(action.geneIds, action.cellline)
        .map(fetchKnockoutsSuccess)
    );

const fetchKnockoutsSuccessEpic = (action$: any) =>
  action$.ofType(FETCH_KNOCKOUTS_SUCCESS)
    .map(() => push('/knockout'));

export default combineEpics(fetchKnockoutsEpic, fetchKnockoutsSuccessEpic);
