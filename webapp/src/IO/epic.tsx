import {
  fetchKnockoutsSuccess,
  fetchKnockoutsFailure,
  FetchKnockouts,
  FetchEdit,
  fetchEditSuccess,
  fetchEditFailure,
  initialLoadSuccess,
  initialLoadFailure
} from "./actions";
import {
  FETCH_KNOCKOUTS,
  FETCH_KNOCKOUTS_SUCCESS,
  FETCH_EDIT,
  INITIAL_LOAD
} from "./actionTypes";
import { Observable } from "rxjs/Observable";
import { combineEpics } from "redux-observable";
import { push } from "react-router-redux";
import { fetchKnockoutsApi, fetchInitialApi, fetchEditApi } from "./api";

const fetchEditEpic = (action$: any) =>
  action$.ofType(FETCH_EDIT).mergeMap((action: FetchEdit) =>
    fetchEditApi(action.geneId, action.editPosition, action.padding)
      .map(fetchEditSuccess)
      .catch((error: string) => Observable.of(fetchEditFailure(error)))
  );

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
  fetchEditEpic,
  fetchKnockoutsSuccessEpic,
  initialLoadEpic
);
