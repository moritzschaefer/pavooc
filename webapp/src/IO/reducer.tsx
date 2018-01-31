import * as t from "./actionTypes";
import { GeneName } from "./actions";

export type State = {
  readonly isFetching: boolean;
  readonly error: string | undefined;
  readonly guides: any | undefined;
  readonly genes: Map<string, string>;
  readonly celllines: Array<string>;
};

const INITIAL_STATE: State = {
  isFetching: false,
  error: undefined,
  guides: undefined,
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
        guides: action.data.map((gene: any) => ({
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
    case t.INITIAL_LOAD:
      return { ...state, isFetching: true, error: undefined };
    case t.INITIAL_LOAD_SUCCESS:
      return {
        ...state,
        isFetching: false,
        error: undefined,
        genes: new Map(
          action.genes.map((g: GeneName) => [g.gene_id, g.gene_symbol])
        ),
        celllines: action.celllines
      };
    case t.SET_GUIDE_SELECTION:
      // TODO slow?
      return {
        ...state,
        guides: state.guides.map((gene: any) => ({
          ...gene,
          guides: gene.guides.map((guide: any, index: number) => ({
            ...guide,
            selected:
              guide.selected !==
              (gene.gene_id === action.geneId && action.guideSelection.includes(index))
          }))
        }))
      };
    case t.TOGGLE_GUIDE_SELECTION:
      // TODO slow?
      return {
        ...state,
        guides: state.guides.map((gene: any) => ({
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
        guides: state.guides.map((gene: any) => ({
          ...gene,
          edited: gene.edited !== (gene.gene_id === action.geneId)
        }))
      };
    default:
      return state;
  }
};
