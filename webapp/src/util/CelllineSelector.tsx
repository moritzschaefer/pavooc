import * as React from "react";
import { connect } from "react-redux";
import { setCellline } from "../App/actions";

import VirtualizedSelect from "react-virtualized-select";

import "./CelllineSelector.css";
import "react-select/dist/react-select.css";

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
    return (
      <div className="cellline-selector">
        <VirtualizedSelect
          options={celllines.map((c: string) => ({ label: c, value: c }))}
          onChange={(cellline: any) => this.props.setCellline(cellline.value)}
          value={{ label: cellline, value: cellline }}
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

export default connect(mapStateToProps, mapDispatchToProps)(CelllineSelector);
