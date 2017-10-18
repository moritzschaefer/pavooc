import * as React from "react";
import { connect } from "react-redux";

import { dismissMessage } from "./actions";

import Button from "material-ui/Button";
import Snackbar from "material-ui/Snackbar";
import IconButton from "material-ui/IconButton";
import CloseIcon from "material-ui-icons/Close";

export interface Props {
  messages: Array<string>;
  dismissMessage: () => {};
}

class Messages extends React.Component<Props> {
  renderSnackBar(message: string) {
    return (
      <Snackbar
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "left"
        }}
        open={!!this.props.messages.length}
        onRequestClose={this.props.dismissMessage}
        autoHideDuration={3000}

        message={<span id="message-id">{message}</span>}
        action={[
          <Button key="undo" color="accent" dense={true}>
            UNDO
          </Button>,
          <IconButton key="close" color="inherit">
            <CloseIcon />
          </IconButton>
        ]}
      />
    );
  }

  render() {
    const { messages } = this.props;
    if (!!messages.length) {
      return this.renderSnackBar(messages[0]);
    } else {
      return null;
    }
  }
}

function mapStateToProps(state: any) {
  return {
    messages: state.messages.messages
  };
}

function mapDispatchToProps(dispatch: any, ownProps: any) {
  return {
    dismissMessage: () => dispatch(dismissMessage())
  };
}

export default connect(mapStateToProps, mapDispatchToProps)(Messages);
