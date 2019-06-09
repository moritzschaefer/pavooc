import * as t from "./actionTypes";

export interface SetGenome {
    type: typeof t.SET_GENOME;
    genome: string;
}

export const setGenome = (genome: string): SetGenome => ({
    type: t.SET_GENOME,
    genome
});

export interface SetCellline {
  type: typeof t.SET_CELLLINE;
  name: string;
}

export const setCellline = (name: string): SetCellline => ({
  type: t.SET_CELLLINE,
  name
});


export interface SetEditPosition {
  type: typeof t.SET_EDIT_POSITION;
  position: number;
}

export const setEditPosition = (position: number): SetEditPosition => ({
  type: t.SET_EDIT_POSITION,
  position
});

export interface SetPadding {
  type: typeof t.SET_PADDING;
  padding: number;
}

export const setPadding = (padding: number): SetPadding => ({
  type: t.SET_PADDING,
  padding
});
