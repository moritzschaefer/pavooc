import { fetchKnockoutsSuccess }  from './actions';
import { FETCH_KNOCKOUTS }  from './actionTypes';
import { Observable } from 'rxjs/Observable';
import { combineEpics } from 'redux-observable';

const fetchKnockoutsApi = (geneIds: any) => {
  const request = fetch(`https://jsonplaceholder.typicode.com/users/${geneIds[0]}`, {method: 'POST'})
    .then(response => response.json());
  return Observable.from(request);
}

const fetchKnockoutsEpic = (action$: any) =>
  action$.ofType(FETCH_KNOCKOUTS)
    .mergeMap((action: any) =>
      fetchKnockoutsApi(action.geneIds)
        .map(fetchKnockoutsSuccess)
    );

export default combineEpics(fetchKnockoutsEpic);
