import {
  fetchKnockoutsSuccess,
  fetchKnockoutsFailure,
  FetchKnockoutsSuccess,
  FetchKnockouts,
  FetchEdit,
  FetchDetails,
  fetchDetailsSuccess,
  fetchDetailsFailure,
  fetchEditSuccess,
  fetchEditFailure,
  initialLoadSuccess,
  initialLoadFailure
} from "./actions";
import {
  FETCH_KNOCKOUTS,
  FETCH_KNOCKOUTS_SUCCESS,
  FETCH_DETAILS_SUCCESS,
  FETCH_DETAILS,
  FETCH_EDIT,
  INITIAL_LOAD
} from "./actionTypes";
import { Observable } from "rxjs/Observable";
import { combineEpics } from "redux-observable";
import { push } from "react-router-redux";
import { fetchDetailsApi, fetchKnockoutsApi, fetchInitialApi, fetchEditApi } from "./api";

const fetchEditEpic = (action$: any) =>
  action$.ofType(FETCH_EDIT).mergeMap((action: FetchEdit) =>
    fetchEditApi(action.geneId, action.editPosition, action.padding)
      .map(fetchEditSuccess)
      .catch((error: string) => Observable.of(fetchEditFailure(error)))
  );

const fetchKnockoutsEpic = (action$: any) =>
  action$.ofType(FETCH_KNOCKOUTS).mergeMap((action: FetchKnockouts) =>
    fetchKnockoutsApi(action.geneIds, action.edit, action.genome)
      .map(fetchKnockoutsSuccess)
      .catch((error: string) => Observable.of(fetchKnockoutsFailure(error)))
  );

const fetchKnockoutsSuccessEpic = (action$: any) =>
  action$
    .ofType(FETCH_KNOCKOUTS_SUCCESS)
    .map((action: FetchKnockoutsSuccess) => {
      if (action.edit) {
        return push("/edit");
      } else {
        return push("/knockout");
      }
    });

const fetchDetailsEpic = (action$: any) =>
  action$.ofType(FETCH_DETAILS).mergeMap((action: FetchDetails) =>
    fetchDetailsApi(action.geneId, action.genome)
      .map(fetchDetailsSuccess)
      .catch((error: string) => Observable.of(fetchDetailsFailure(error)))
  );

const fetchDetailsSuccessEpic = (action$: any) =>
  action$
    .ofType(FETCH_DETAILS_SUCCESS)
    .map(() =>
        push(`/edit`)
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
  fetchDetailsEpic,
  fetchKnockoutsSuccessEpic,
  fetchDetailsSuccessEpic,
  initialLoadEpic
);
