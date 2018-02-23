import * as React from "react";
import { connect } from "react-redux";
import { setCellline } from "../App/actions";

import Typography from "material-ui/Typography";
import Input from "material-ui/Input";
import { MenuItem } from "material-ui/Menu";
import ArrowDropDownIcon from "material-ui-icons/ArrowDropDown";
import ArrowDropUpIcon from "material-ui-icons/ArrowDropUp";
import ClearIcon from "material-ui-icons/Clear";
import Chip from "material-ui/Chip";
import Select from "react-select";
import "./CelllineSelector.css";
import "react-select/dist/react-select.css";

class Option extends React.Component<any, any> {
  handleClick = (event: any) => {
    this.props.onSelect(this.props.option, event);
  };

  render() {
    const { children, isFocused, isSelected, onFocus } = this.props;

    return (
      <MenuItem
        onFocus={onFocus}
        selected={isFocused}
        onClick={this.handleClick}
        component="div"
        style={{
          fontWeight: isSelected ? 500 : 400
        }}
      >
        {children}
      </MenuItem>
    );
  }
}

function SelectWrapped(props: any) {
  const { ...other } = props;

  return (
    <Select
      optionComponent={Option}
      noResultsText={<Typography>{"No results found"}</Typography>}
      arrowRenderer={(arrowProps: any) => {
        return arrowProps.isOpen ? <ArrowDropUpIcon /> : <ArrowDropDownIcon />;
      }}
      clearRenderer={() => <ClearIcon />}
      valueComponent={(valueProps: any) => {
        const { children, onRemove } = valueProps; // value normally

        {
          /* const onDelete = (event: any) => { */
        }
        {
          /*   event.preventDefault(); */
        }
        {
          /*   event.stopPropagation(); */
        }
        {
          /*   onRemove(value); */
        }
        {
          /* }; */
        }
        {
          /*  */
        }
        if (onRemove) {
          return <Chip tabIndex={-1} label={children} className="cl-chip" />;
        }

        return <div className="Select-value">{children}</div>;
      }}
      {...other}
    />
  );
}

interface Props {
  cellline: string;
  celllines: Array<string>;
  setCellline: (cellline: string) => {};
}

interface State {}

class CelllineSelector extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
  }

  render() {
    const { celllines, cellline } = this.props;
    const inputProps: any = {
      value: cellline,
      onChange: this.props.setCellline,
      placeholder: "Select single-value…",
      instanceId: "react-select-single",
      id: "react-select-single",
      name: "react-select-single",
      simpleValue: true,
      options: celllines.map((c: string) => ({ label: c, value: c }))
    };
    return (
      <div className="cellline-selector">
        <Input
          fullWidth={true}
          inputComponent={SelectWrapped}
          inputProps={inputProps}
        />
      </div>
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
