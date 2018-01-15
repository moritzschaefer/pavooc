import {
  fetchKnockoutsSuccess,
  fetchKnockoutsFailure,
  FetchKnockouts,
  initialLoadSuccess,
  initialLoadFailure
} from "./actions";
import {
  FETCH_KNOCKOUTS,
  FETCH_KNOCKOUTS_SUCCESS,
  INITIAL_LOAD
} from "./actionTypes";
import { Observable } from "rxjs/Observable";
import { combineEpics } from "redux-observable";
import { push } from "react-router-redux";
import { fetchKnockoutsApi, fetchInitialApi } from "./api";

const fetchKnockoutsEpic = (action$: any) =>
  action$.ofType(FETCH_KNOCKOUTS).mergeMap((action: FetchKnockouts) =>
    fetchKnockoutsApi(action.geneIds)
      .map(fetchKnockoutsSuccess)
      .catch((error: string) => Observable.of(fetchKnockoutsFailure(error)))
  );

const fetchKnockoutsSuccessEpic = (action$: any) =>
  action$
    .ofType(FETCH_KNOCKOUTS_SUCCESS)
    .map(() =>
        push("/knockout")
    );

const initialLoadEpic = (action$: any) =>
  action$.ofType(INITIAL_LOAD).mergeMap(() =>
    fetchInitialApi()
      .map(initialLoadSuccess)
      .catch((error: string) => Observable.of(initialLoadFailure(error)))
  );

export default combineEpics(
  fetchKnockoutsEpic,
  fetchKnockoutsSuccessEpic,
  initialLoadEpic
);
