import * as t from "./actionTypes";

export interface SetGuideCount {
  type: typeof t.SET_GUIDE_COUNT;
  guideCount: number;
}

export interface SetCellline {
  type: typeof t.SET_CELLLINE;
  name: string;
}

export const setCellline = (name: string): SetCellline => ({
  type: t.SET_CELLLINE,
  name
});

export const setGuideCount = (guideCount: number): SetGuideCount => ({
  type: t.SET_GUIDE_COUNT,
  guideCount
});
