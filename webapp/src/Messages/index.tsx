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
  render() {
    const { messages } = this.props;
    return (
      <Snackbar
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "left"
        }}
        open={!!messages.length}
        onRequestClose={this.props.dismissMessage}
        autoHideDuration={3000}
        message={<span id="message-id">{messages[0] || ""}</span>}
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
