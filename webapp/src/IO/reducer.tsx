import * as t from "./actionTypes";

import { guidesWithDomains } from "../util/functions";

export type State = {
  readonly isFetching: boolean;
  readonly error: string | undefined;
  readonly knockoutData: any | undefined;
  readonly genes: Map<string, string>;
  readonly celllines: Array<string>;
  readonly editData: any;
  readonly detailsData: any;
  readonly guideCount: number;
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

const INITIAL_EDIT_DATA = {
  guidesBefore: [],
  guidesAfter: []
};

const INITIAL_STATE: State = {
  isFetching: false,
  error: undefined,
  knockoutData: undefined,
  editData: INITIAL_EDIT_DATA,
  detailsData: {},
  genes: new Map<string, string>(),
  celllines: [],
  guideCount: 5
};

export default (state: State = INITIAL_STATE, action: any) => {
  switch (action.type) {
    case t.SET_GUIDE_COUNT:
      return { ...state, guideCount: action.guideCount };
    case t.FETCH_KNOCKOUTS:
      return { ...state, isFetching: true, error: undefined };
    case t.FETCH_KNOCKOUTS_SUCCESS:
      return {
        ...state,
        isFetching: false,
        error: undefined,
        knockoutData: action.data.map((gene: any) => {
          if (action.edit) {
            return {
              ...gene,
              guides: gene.guides.map((guide: any, index: number) => ({
                ...guide,
                selected: false
              }))
            };
          }
          const sortedGuides = guidesWithDomains(
            gene
          ).map((guide: any, index: number) => [guide, index]);
          sortedGuides.sort(function(a: [any, number], b: [any, number]) {
            // domain gives a bonus of 0.1
            let bScore =
              b[0].scores.pavooc * 0.6 +
              (1 - b[0].scores.Doench2016CFDScore) * 0.3;
            if (b[0].domains.length > 0) {
              bScore += 0.1;
            }
            let aScore =
              a[0].scores.pavooc * 0.6 +
              (1 - a[0].scores.Doench2016CFDScore) * 0.3;
            if (a[0].domains.length > 0) {
              aScore += 0.1;
            }
            return bScore - aScore;
          });
          let selectedGuideIndices = sortedGuides
            .slice(0, state.guideCount)
            .map(([guide, index]: [any, number]) => index);

          return {
            ...gene,
            guides: gene.guides.map((guide: any, index: number) => ({
              ...guide,
              selected: selectedGuideIndices.includes(index)
            }))
          };
        })
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
      return {
        ...state,
        isFetching: true,
        error: undefined,
        editData: INITIAL_EDIT_DATA
      };
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
        editData: INITIAL_EDIT_DATA
      };
    case t.SET_EDIT_SELECTION:
      let { guidesBefore, guidesAfter } = state.editData;
      if (action.beforeNotAfter) {
        guidesBefore = guidesBefore;
      }
      return {
        ...state,
        editData: {
          ...state.editData,
          guidesBefore: guidesBefore.map((guide: any, index: number) => ({
            ...guide,
            selected:
              (action.beforeNotAfter &&
                action.guideSelection.includes(index)) ||
              (!action.beforeNotAfter && guide.selected)
          })),
          guidesAfter: guidesAfter.map((guide: any, index: number) => ({
            ...guide,
            selected:
              (!action.beforeNotAfter &&
                action.guideSelection.includes(index)) ||
              (action.beforeNotAfter && guide.selected)
          }))
        }
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
              (gene.gene_id === action.geneId &&
                action.guideSelection.includes(index)) ||
              (guide.selected && gene.gene_id !== action.geneId)
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
          ...gene
        }))
      };
    default:
      return state;
  }
};
