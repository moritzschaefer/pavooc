import * as t from "./actionTypes";

export type State = {
  readonly messages: Array<string>;
};

const INITIAL_STATE: State = {
  messages: []
};

export default (state: State = INITIAL_STATE, action: any) => {
  const messages = [...state.messages];
  switch (action.type) {
    case t.SHOW_MESSAGE:
      messages.push(action.message);
      return { ...state, messages };
    case t.DISMISS_MESSAGE:
      // delete first element of array
      messages.shift();
      return { ...state, messages };
    default:
      return state;
  }
};
