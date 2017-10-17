import * as t from './actionTypes';

export interface FetchKnockouts {
  type: typeof t.FETCH_KNOCKOUTS;
  geneIds: Array<string>;
  cellline: string
}

export const fetchKnockouts = (geneIds: Array<string>, cellline: string) : FetchKnockouts => ({
  type: t.FETCH_KNOCKOUTS,
  geneIds,
  cellline
});

export interface FetchKnockoutsFailure {
  type: typeof t.FETCH_KNOCKOUTS_FAILURE;
  error: string
}

export const fetchKnockoutsFailure = (error: string): FetchKnockoutsFailure => ({
  type: t.FETCH_KNOCKOUTS_FAILURE,
  error
})

export interface FetchKnockoutsSuccess {
  type: typeof t.FETCH_KNOCKOUTS_SUCCESS;
  data: object
}

export const fetchKnockoutsSuccess = (payload: object ): FetchKnockoutsSuccess => ({
  type: t.FETCH_KNOCKOUTS_SUCCESS,
  data: payload
})
