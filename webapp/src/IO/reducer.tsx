import * as t from "./actionTypes";

export type State = {
  readonly isFetching: boolean;
  readonly error: string | undefined;
  readonly knockoutData: any | undefined;
  readonly genes: Map<string, string>;
  readonly celllines: Array<string>;
  readonly editData: any;
  readonly detailsData: any;
};

export interface Gene {
  gene_id: string;
  gene_symbol: string;
  strand: string;
  start: number;
  end: number;
  chromosome: string;
  pdbs: Array<any>;
  exons: Array<any>;
}

const INITIAL_STATE: State = {
  isFetching: false,
  error: undefined,
  knockoutData: undefined,
  editData: {},
  detailsData: {},
  genes: new Map<string, string>(),
  celllines: []
};

export default (state: State = INITIAL_STATE, action: any) => {
  switch (action.type) {
    case t.FETCH_KNOCKOUTS:
      return { ...state, isFetching: true, error: undefined };
    case t.FETCH_KNOCKOUTS_SUCCESS:
      return {
        ...state,
        isFetching: false,
        error: undefined,
        // just add selected:false to every guide and edited:false to every gene
        knockoutData: action.data.map((gene: any) => ({
          ...gene,
          edited: false,
          guides: gene.guides.map((guide: any) => ({
            ...guide,
            selected: false
          }))
        }))
      };
    case t.FETCH_KNOCKOUTS_FAILURE:
      return { ...state, isFetching: false, error: action.error };
    case t.FETCH_DETAILS:
      return { ...state, isFetching: true, error: undefined };
    case t.FETCH_DETAILS_SUCCESS:
      return {
        ...state,
        isFetching: false,
        error: undefined,
        detailsData: action.data
      };
    case t.FETCH_DETAILS_FAILURE:
      return { ...state, isFetching: false, error: action.error };
    case t.FETCH_EDIT:
      return { ...state, isFetching: true, error: undefined };
    case t.FETCH_EDIT_SUCCESS:
      return {
        ...state,
        isFetching: false,
        error: undefined,
        editData: action.data
      };
    case t.FETCH_EDIT_FAILURE:
      return { ...state, isFetching: false, error: action.error };
    case t.INITIAL_LOAD:
      return { ...state, isFetching: true, error: undefined };
    case t.INITIAL_LOAD_SUCCESS:
      return {
        ...state,
        isFetching: false,
        error: undefined,
        genes: new Map(
          action.genes.map((g: any) => [g.gene_id, g.gene_symbol])
        ),
        celllines: action.celllines,
        editData: {}
      };
    case t.SET_GUIDE_SELECTION:
      // TODO slow?
      return {
        ...state,
        knockoutData: state.knockoutData.map((gene: any) => ({
          ...gene,
          guides: gene.guides.map((guide: any, index: number) => ({
            ...guide,
            selected:
              ((gene.gene_id === action.geneId) && action.guideSelection.includes(index)) ||
              ((guide.selected && (gene.gene_id !== action.geneId)))
          }))
        }))
      };
    case t.TOGGLE_GUIDE_SELECTION:
      // TODO slow?, and..
      return {
        ...state,
        knockoutData: state.knockoutData.map((gene: any) => ({
          ...gene,
          guides: gene.guides.map((guide: any, index: number) => ({
            ...guide,
            selected:
              guide.selected !==
              (gene.gene_id === action.geneId && index === action.guideIndex)
          }))
        }))
      };
    case t.MARK_GENE_EDIT:
      return {
        ...state,
        knockoutData: state.knockoutData.map((gene: any) => ({
          ...gene,
          edited: gene.edited !== (gene.gene_id === action.geneId)
        }))
      };
    default:
      return state;
  }
};
