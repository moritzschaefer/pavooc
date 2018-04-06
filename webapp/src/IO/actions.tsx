import * as t from "./actionTypes";

export interface FetchKnockouts {
  type: typeof t.FETCH_KNOCKOUTS;
  geneIds: Array<string>;
  edit: boolean;
}

export const fetchKnockouts = (
  geneIds: Array<string>,
  edit: boolean = false
): FetchKnockouts => ({
  type: t.FETCH_KNOCKOUTS,
  edit,
  geneIds
});

export interface FetchKnockoutsFailure {
  type: typeof t.FETCH_KNOCKOUTS_FAILURE;
  error: string;
}

export const fetchKnockoutsFailure = (
  error: string
): FetchKnockoutsFailure => ({
  type: t.FETCH_KNOCKOUTS_FAILURE,
  error
});

export interface FetchKnockoutsSuccess {
  type: typeof t.FETCH_KNOCKOUTS_SUCCESS;
  data: object;
  edit: boolean;
}

export const fetchKnockoutsSuccess = (
  payload: any
): FetchKnockoutsSuccess => ({
  type: t.FETCH_KNOCKOUTS_SUCCESS,
  data: payload,
  edit: payload.length === 1 && payload[0].sequence // if payload contains the sequence field, then it was an edit request
});

export interface FetchEdit {
  type: typeof t.FETCH_EDIT;
  geneId: string;
  editPosition: number;
  padding: number;
}

export const fetchEdit = (
  geneId: string,
  editPosition: number,
  padding: number
): FetchEdit => ({
  type: t.FETCH_EDIT,
  geneId,
  editPosition,
  padding
});

export interface FetchEditFailure {
  type: typeof t.FETCH_EDIT_FAILURE;
  error: string;
}

export const fetchEditFailure = (
  error: string
): FetchEditFailure => ({
  type: t.FETCH_EDIT_FAILURE,
  error
});

export interface FetchEditSuccess {
  type: typeof t.FETCH_EDIT_SUCCESS;
  data: object;
}

export const fetchEditSuccess = (
  payload: object
): FetchEditSuccess => ({
  type: t.FETCH_EDIT_SUCCESS,
  data: payload
});

export interface FetchDetails {
  type: typeof t.FETCH_DETAILS;
  geneId: string;
}

export const fetchDetails = (
  geneId: string,
): FetchDetails => ({
  type: t.FETCH_DETAILS,
  geneId
});

export interface FetchDetailsFailure {
  type: typeof t.FETCH_DETAILS_FAILURE;
  error: string;
}

export const fetchDetailsFailure = (
  error: string
): FetchDetailsFailure => ({
  type: t.FETCH_DETAILS_FAILURE,
  error
});

export interface FetchDetailsSuccess {
  type: typeof t.FETCH_DETAILS_SUCCESS;
  data: object;
}

export const fetchDetailsSuccess = (
  payload: object
): FetchDetailsSuccess => ({
  type: t.FETCH_DETAILS_SUCCESS,
  data: payload
});

export interface InitialLoad {
  type: typeof t.INITIAL_LOAD;
}

export const initialLoad = (): InitialLoad => ({
  type: t.INITIAL_LOAD
});

export interface InitialLoadSuccess {
  type: typeof t.INITIAL_LOAD_SUCCESS;
  genes: Array<{gene_id: string, gene_symbol: string}>;
  celllines: Array<string>;
}

export const initialLoadSuccess = ({
  genes,
  celllines
}: any): InitialLoadSuccess => ({
  type: t.INITIAL_LOAD_SUCCESS,
  genes,
  celllines
});

export interface InitialLoadFailure {
  type: typeof t.INITIAL_LOAD_FAILURE;
  error: string;
}

export const initialLoadFailure = (error: string): InitialLoadFailure => ({
  type: t.INITIAL_LOAD_FAILURE,
  error
});

export interface SetGuideSelection {
  type: typeof t.SET_GUIDE_SELECTION;
  geneId: string;
  guideSelection: number[];
}

export const setGuideSelection = (geneId: string, guideSelection: number[]): SetGuideSelection => ({
  type: t.SET_GUIDE_SELECTION,
  geneId,
  guideSelection
});

export interface ToggleGuideSelection {
  type: typeof t.TOGGLE_GUIDE_SELECTION;
  geneId: string;
  guideIndex: number;
}

export const toggleGuideSelection = (geneId: string, guideIndex: number): ToggleGuideSelection => ({
  type: t.TOGGLE_GUIDE_SELECTION,
  geneId,
  guideIndex
});

export interface MarkGeneEdit {
  type: typeof t.MARK_GENE_EDIT;
  geneId: string;
}

export const markGeneEdit = (geneId: string) : MarkGeneEdit => ({
  type: t.MARK_GENE_EDIT,
  geneId
});

