import * as t from "./actionTypes";

interface State {
  readonly cellline: string;
}

const INITIAL_STATE: State = {
  cellline: ''
};

export default (state: State = INITIAL_STATE, action: any) => {
  switch (action.type) {
    case t.SET_CELLLINE:
      return { ...state, cellline: action.name };
    default:
      return state;
  }
};
