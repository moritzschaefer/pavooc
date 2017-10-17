import * as t from './actionTypes';

export type State = {
  readonly isFetching: boolean,
  readonly error: string | undefined,
  readonly data: object | undefined
};

const INITIAL_STATE: State = {
  isFetching: false,
  error: undefined,
  data: undefined
};


export default (state : State = INITIAL_STATE, action: any) => {
  switch (action.type) {
    case t.FETCH_KNOCKOUTS:
      return { ...state, isFetching: true, error: undefined };
    case t.FETCH_KNOCKOUTS_SUCCESS:
      return { ...state, isFetching: false, error: undefined, data: action.data };
    case t.FETCH_KNOCKOUTS_FAILURE:
      return { ...state, isFetching: false, error: action.error };
    default:
      return state;
  }
}
