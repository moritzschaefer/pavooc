import * as t from "./actionTypes";

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

export interface InitialLoad {
  type: typeof t.INITIAL_LOAD;
}

export const initialLoad = (): InitialLoad => ({
  type: t.INITIAL_LOAD
});

export interface GeneName {
  gene_id: string;
  gene_symbol: string;
}

export interface InitialLoadSuccess {
  type: typeof t.INITIAL_LOAD_SUCCESS;
  genes: Array<GeneName>;
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

