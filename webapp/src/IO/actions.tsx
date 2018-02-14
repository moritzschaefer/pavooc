import * as t from "./actionTypes";
import { Gene } from "./reducer";

export interface FetchKnockouts {
  type: typeof t.FETCH_KNOCKOUTS;
  geneIds: Array<string>;
}

export const fetchKnockouts = (
  geneIds: Array<string>
): FetchKnockouts => ({
  type: t.FETCH_KNOCKOUTS,
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
}

export const fetchKnockoutsSuccess = (
  payload: object
): FetchKnockoutsSuccess => ({
  type: t.FETCH_KNOCKOUTS_SUCCESS,
  data: payload
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



export interface InitialLoad {
  type: typeof t.INITIAL_LOAD;
}

export const initialLoad = (): InitialLoad => ({
  type: t.INITIAL_LOAD
});

export interface InitialLoadSuccess {
  type: typeof t.INITIAL_LOAD_SUCCESS;
  genes: Array<Gene>;
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

export const setGuideSelection = (geneId: string, guideSelection: number[]) : SetGuideSelection => ({
  type: t.SET_GUIDE_SELECTION,
  geneId,
  guideSelection
});


export interface ToggleGuideSelection {
  type: typeof t.TOGGLE_GUIDE_SELECTION;
  geneId: string;
  guideIndex: number;
}

export const toggleGuideSelection = (geneId: string, guideIndex: number) : ToggleGuideSelection => ({
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

