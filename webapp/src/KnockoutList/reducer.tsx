import * as t from "./actionTypes";

interface State {
  readonly guideCount: number;
  readonly cellline: string;
}

const INITIAL_STATE: State = {
  guideCount: 5,
  cellline: ''
};

export default (state: State = INITIAL_STATE, action: any) => {
  switch (action.type) {
    case t.SET_CELLLINE:
      return { ...state, cellline: action.name };
    case t.SET_GUIDE_COUNT:
      return { ...state, guideCount: action.guideCount };
    default:
      return state;
  }
};
