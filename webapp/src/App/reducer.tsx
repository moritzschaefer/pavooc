import * as t from "./actionTypes";

interface State {
  readonly cellline: string;
  readonly padding: number;
  readonly editPosition: number;
  readonly genome: string;
}

const INITIAL_STATE: State = {
    cellline: "",
    genome: "",
  padding: 100,
  editPosition: -1
};

export default (state: State = INITIAL_STATE, action: any) => {
  switch (action.type) {
    case t.SET_GENOME:
        return { ...state, genome: action.genome };
    case t.SET_CELLLINE:
      return { ...state, cellline: action.name };
    case t.SET_EDIT_POSITION:
      return { ...state, editPosition: action.position };
    case t.SET_PADDING:
      return { ...state, padding: action.padding };

    default:
      return state;
  }
};
