import * as React from "react";
import { connect } from "react-redux";
import { setCellline } from "../App/actions";

import Downshift from "downshift";
import TextField from "material-ui/TextField";
import Paper from "material-ui/Paper";
import { MenuItem } from "material-ui/Menu";
// import { withStyles } from "material-ui/styles";

interface Props {
  cellline: string;
  celllines: Array<string>;
  setCellline: (cellline: string) => {};
}

interface State {
  inputValue: string;
  menuIsOpen: boolean;
}

class CelllineSelector extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      menuIsOpen: false,
      inputValue: ""
    };
  }

  renderInput(value: string) {
    return <TextField autoFocus={false} className="autoInput" value={value} />;
  }

  renderSuggestion(
    item: string,
    selected: boolean,
    highlighted: boolean,
    itemProps: object
  ) {
    return (
      <MenuItem
        {...itemProps}
        selected={highlighted}
        component="div"
        key={item}
      >
        <div>{item}</div>
      </MenuItem>
    );
  }

  onInputChange = ({
    inputValue,
    highlightedIndex
  }: {
    inputValue: string;
    highlightedIndex: number | undefined;
  }) => {
    if (typeof inputValue !== "string") {
      if (typeof highlightedIndex === "undefined") {
        this.setState({ menuIsOpen: false });
      }
      return;
    }
    this.setState({ inputValue });

    if (this.props.celllines.includes(inputValue)) {
      this.props.setCellline(inputValue);
      this.setState({ menuIsOpen: false });
    }
  };

  onChange = (selected: any, stateAndHelpers: object | undefined) => {
    this.onInputChange(selected);
  };

  render() {
    // onOuterClick={() => this.setState({menuIsOpen: false})}
    // TODO support lowercase
    const { celllines } = this.props;
    const { inputValue, menuIsOpen } = this.state;
    return (
      <Downshift
        isOpen={menuIsOpen}
        inputValue={inputValue}
        onChange={this.onChange}
        onStateChange={this.onInputChange}
      >
        {({
          getInputProps,
          getLabelProps,
          getItemProps,
          highlightedIndex,
          selectedItem
        }) => {
          return (
            <div>
              <TextField
                inputProps={getInputProps()}
                label={"Cancer celllines"}
                value={inputValue || undefined}
                onFocusCapture={() =>
                  this.setState({ menuIsOpen: true })}
              />
              {menuIsOpen ? (
                <Paper className="suggestionContainer">
                  {Array.from(celllines)
                    .filter(
                      e =>
                        !inputValue ||
                        e.includes(inputValue.toUpperCase())
                    ).slice(0, 50)
                    .map((item, index) =>
                      this.renderSuggestion(
                        item,
                        selectedItem === item,
                        highlightedIndex === index,
                        getItemProps({ index, item: item })
                      )
                    )}
                </Paper>
              ) : null}
            </div>
          );
        }}
      </Downshift>
    );
  }
}

const mapStateToProps = (state: any) => ({
  cellline: state.app.cellline,
  celllines: state.io.celllines
});

const mapDispatchToProps = (dispatch: any) => ({
  setCellline: (cellline: string) => dispatch(setCellline(cellline))
});

// export default connect(mapStateToProps, mapDispatchToProps)(
//   withStyles(styles, { withTheme: true })(CelllineSelector)
// );

export default connect(mapStateToProps, mapDispatchToProps)(CelllineSelector);
