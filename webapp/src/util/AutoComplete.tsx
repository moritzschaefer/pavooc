// this class, unfortunately, is not very generic...
import * as React from "react";
import Downshift from "downshift";
import Paper from "material-ui/Paper";
import { MenuItem } from "material-ui/Menu";
import TextField from "material-ui/TextField";
import "./AutoComplete.css";

interface Props {
  onSelect: ((selected: string) => boolean) | undefined;
  dataSource: Map<string, string>;
  dataSourceReverse: Map<string, string> | undefined;
  floatingLabelText: string;
  openOnFocus: boolean;
  deleteOnSelect: boolean;
  onMessage: ((message: string) => {}) | null;
}

interface State {
  menuIsOpen: boolean;
  inputValue: string;
}

export default class AutoComplete extends React.Component<Props, State> {
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
    item: Array<string>,
    selected: boolean,
    highlighted: boolean,
    itemProps: object
  ) {
    return (
      <MenuItem
        {...itemProps}
        selected={highlighted}
        component="div"
        key={item[0]}
      >
        <div>{item[1]}</div>
      </MenuItem>
    );
  }

  // Check if a value or key is the input and return the corresponding key or undefined
  getKeyForInput(upperInput: string) {
    // TODO speedup!!
    const { dataSource, dataSourceReverse } = this.props;

    // TODO dataSource values must be uppercase
    if (dataSource.get(upperInput)) {
      return upperInput;
    }
    return dataSourceReverse && dataSourceReverse.get(upperInput);
  }

  onInputChange = ({
    inputValue,
    highlightedIndex
  }: {
    inputValue: string;
    highlightedIndex: number | undefined;
  }) => {
    const { onSelect, deleteOnSelect, onMessage } = this.props;
    if (typeof inputValue !== "string") {
      if (typeof highlightedIndex === "undefined") {
        this.setState({ menuIsOpen: false });
      }
      return;
    }
    if (!onSelect) {
      this.setState({ inputValue });
      return;
    }
    let results: Array<string> = [];
    const upperInput = inputValue.toUpperCase();
    if (upperInput.includes(",")) {
      // comma separated list
      results = upperInput.split(",");
    } else if (upperInput.includes(" ")) {
      results = upperInput.split(" ");
      // results = [for (let v of results) v.trim()];
    } else {
      const key = this.getKeyForInput(upperInput);
      if (key) {
        this.onChange(key, undefined);
        if (!deleteOnSelect) {
          this.setState({ inputValue });
        }
      } else {
        // this is the usual case
        this.setState({ inputValue });
      }
    }

    if (results.length > 0) {
      let added = 0;
      let invalid = 0;
      let duplicate = 0;
      for (let result of results) {
        const key = this.getKeyForInput(result);
        if (key) {
          if (onSelect(key)) {
            added++;
          } else {
            duplicate++;
          }
        } else {
          invalid++;
        }
      }

      if (onMessage) {
        onMessage(
          `Added ${added} genes. ${duplicate} already selected, ${invalid} unrecognized.`
        );
      }
      if (added > 0 && deleteOnSelect) {
        // TODO use Toast
        this.setState({ inputValue: "" });
      } else {
        this.setState({ inputValue });
      }
    }
  };

  onChange = (selected: any, stateAndHelpers: object | undefined) => {
    const { onSelect, deleteOnSelect } = this.props;
    this.setState({ menuIsOpen: false });
    if (onSelect) { // TODO onSelect is called twice :/
      onSelect(selected);
      if (deleteOnSelect) {
        this.setState({ inputValue: "" });
      }
    }
  };

  render() {
    // onOuterClick={() => this.setState({menuIsOpen: false})}
    // TODO support lowercase
    const { dataSource, floatingLabelText, openOnFocus } = this.props;
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
                label={floatingLabelText}
                value={inputValue || undefined}
                onFocusCapture={() =>
                  this.setState({ menuIsOpen: openOnFocus || menuIsOpen })}
              />
              {menuIsOpen ? (
                <Paper className="suggestionContainer">
                  {Array.from(dataSource.entries())
                    .filter(
                      e =>
                        !inputValue ||
                        e[0].includes(inputValue.toUpperCase()) ||
                        e[1].includes(inputValue.toUpperCase())
                    )
                    .map((item, index) =>
                      this.renderSuggestion(
                        item,
                        selectedItem === item[0],
                        highlightedIndex === index,
                        getItemProps({ index, item: item[0] })
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
