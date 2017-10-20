import * as t from "./actionTypes";

export interface SetGuideCount {
  type: typeof t.SET_GUIDE_COUNT;
  guideCount: number;
}

export const setGuideCount = (guideCount: number): SetGuideCount => ({
  type: t.SET_GUIDE_COUNT,
  guideCount
});
