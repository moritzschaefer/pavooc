import * as t from "./actionTypes";

export interface SetCellline {
  type: typeof t.SET_CELLLINE;
  name: string;
}

export const setCellline = (name: string): SetCellline => ({
  type: t.SET_CELLLINE,
  name
});
