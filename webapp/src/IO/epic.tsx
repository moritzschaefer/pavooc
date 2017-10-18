import {
  fetchKnockoutsSuccess,
  FetchKnockouts,
  initialLoadSuccess
} from "./actions";
import {
  FETCH_KNOCKOUTS,
  FETCH_KNOCKOUTS_SUCCESS,
  INITIAL_LOAD
} from "./actionTypes";
import { showMessage } from "../Messages/actions";
import { Observable } from "rxjs/Observable";
import { combineEpics } from "redux-observable";
import { push } from "react-router-redux";

const fetchKnockoutsApi = (geneIds: any, cellline: string) => {
  const request = fetch(`/api/knockout`, {
    method: "POST",
    body: JSON.stringify({ gene_ids: geneIds })
  }).then(response => response.json());
  return Observable.from(request);
};

const fetchInitialApi = () => {
  const request = fetch(`/api/initial`, { method: "GET" }).then(response =>
    response.json()
  );
  return Observable.from(request);
};

const fetchKnockoutsEpic = (action$: any) =>
  action$
    .ofType(FETCH_KNOCKOUTS)
    .mergeMap((action: FetchKnockouts) =>
      fetchKnockoutsApi(action.geneIds, action.cellline).map(
        fetchKnockoutsSuccess
      )
    );

const fetchKnockoutsSuccessEpic = (action$: any) =>
  action$
    .ofType(FETCH_KNOCKOUTS_SUCCESS)
    .flatMap(() =>
      Observable.concat(
        Observable.of(push("/knockout")),
        Observable.of(showMessage("Successfully downloaded"))
      )
    );

const initialLoadEpic = (action$: any) =>
  action$
    .ofType(INITIAL_LOAD)
    .mergeMap(() => fetchInitialApi().map(initialLoadSuccess));

export default combineEpics(
  fetchKnockoutsEpic,
  fetchKnockoutsSuccessEpic,
  initialLoadEpic
);
