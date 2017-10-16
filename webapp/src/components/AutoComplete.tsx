import * as React from 'react';
import Downshift from 'downshift';
import Paper from 'material-ui/Paper';
import { MenuItem } from 'material-ui/Menu';
import TextField from 'material-ui/TextField';

interface Props {
  onSelect: ((selected: string) => boolean) | undefined;
  dataSource: Array<string>;
  floatingLabelText: string;
  openOnFocus: boolean;
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
      inputValue: ''
    };
  }

  renderInput(value: string) {
    return (
      <TextField
        autoFocus={false}
        className="autoInput"
        value={value}
      />
    );
  }

  renderSuggestion(item: string, selected: boolean, highlighted: boolean, itemProps: object) {
    return (
      <MenuItem {...itemProps} selected={highlighted} component="div" key={item}>
        <div>
          {item}
        </div>
      </MenuItem>
    );
  }

  onInputChange = ({ inputValue }: any) => {
    const { onSelect, dataSource } = this.props;
    if (typeof inputValue !== 'string') {
      return;
    }
    if (!onSelect) {
      this.setState({ inputValue });
      return;
    }
    let results: Array<string> = [];
    const upperInput = inputValue.toUpperCase();
    if (upperInput.includes(',')) {
      // comma separated list
      results = upperInput.split(',');
    } else if(upperInput.includes(' ')) {
      results = upperInput.split(' ');
      //results = [for (let v of results) v.trim()]; m
    } else {
      if (dataSource.find(v => v.toUpperCase() === upperInput)) {
        this.onChange(upperInput, undefined);
      } else {
        // this is the usual case
        this.setState({ inputValue: inputValue });
      }
    }

    if(results.length > 0) {
      let added = 0;
      let invalid = 0;
      let duplicate = 0;
      for(let result of results) {
        if(dataSource.find(v => v.toUpperCase() === result)) {
          if(onSelect(result)) {
            added++;
          } else {
            duplicate++;
          }
        } else {
          invalid++;
        }
      }

      console.log(`Added ${added} genes. ${duplicate} already selected, ${invalid} unrecognized.`);
      if(added > 0) {
        // TODO use Toast
        this.setState({ inputValue: '' });
      } else {
        this.setState({ inputValue });
      }
    }
  }

  onChange = (selected: any, stateAndHelpers: object | undefined) => {
    const { onSelect } = this.props;
    this.setState({ menuIsOpen: false });
    if (onSelect) {
      this.setState({ inputValue: '' });
      onSelect(selected);
    }
  }

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
          selectedItem,
          inputValue
          }) => {
            return (
            <div>
              <TextField
                inputProps={getInputProps()}
                label={floatingLabelText}
                value={inputValue || undefined}
                onFocusCapture={() => this.setState({menuIsOpen: openOnFocus})}
              />
              {menuIsOpen ? (
                <Paper>
                  {dataSource
                    .filter(i => !inputValue || i.includes(inputValue))
                    .map((item, index) =>
                      this.renderSuggestion(item, selectedItem === item, highlightedIndex === index, getItemProps({index, item}))
                    )}
                </Paper>
              ) : (
                null
              )}
            </div>
            )
          }
        }
      </Downshift>
      );
  }
}
