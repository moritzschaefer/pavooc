import * as t from "./actionTypes";

type ShowMessage = {
  message: string,
  type: typeof t.SHOW_MESSAGE
}

export const showMessage = (message: string): ShowMessage => ({
  type: t.SHOW_MESSAGE,
  message
})

type DismissMessage = {
  type: typeof t.DISMISS_MESSAGE
}

export const dismissMessage = (): DismissMessage => ({
  type: t.DISMISS_MESSAGE,
})
