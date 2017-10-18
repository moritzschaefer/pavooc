import * as React from "react";
import AutoComplete from "../util/AutoComplete";
import Radio, { RadioGroup } from "material-ui/Radio";
import { FormControlLabel } from "material-ui/Form";
import Button from "material-ui/Button";
import Chip from "material-ui/Chip";
import "./Form.css";

export interface Props {
  go: (geneSelection: Array<string>, cellline: string) => {};
  initialLoad: () => {};
  geneIds: Array<string>;
  celllines: Array<string>;
  className: string;
}

export interface State {
  cellline: string;
  geneSelection: Array<string>;
  experimentType: string;
}

export default class Form extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      cellline: "UM-UC-3",
      experimentType: "knockout",
      geneSelection: ["ENSG00000015475.14", "ENSG00000070010.14"]
    };
  }
  componentDidMount() {
    this.props.initialLoad();
  }

  _setExperimentType = (event: any) => {
    this.setState({ experimentType: event.target.value });
  };

  addGene = (gene: string) => {
    if (this.state.geneSelection.find(v => v === gene)) {
      return false;
    }
    const geneSelection = [...this.state.geneSelection];
    geneSelection.push(gene);
    this.setState({ geneSelection: geneSelection });
    return true;
  };

  selectCellline = (cellline: string): boolean => {
    this.setState({ cellline });
    return true;
  };

  removeGene = (data: string) => {
    const geneSelection = [...this.state.geneSelection];
    const chipToDelete = geneSelection.indexOf(data);
    geneSelection.splice(chipToDelete, 1);
    this.setState({ geneSelection });
  };

  renderChip(data: string) {
    return (
      <Chip
        label={data}
        key={data}
        onRequestDelete={this.removeGene}
        className="geneChip"
      />
    );
  }

  render() {
    const { geneIds, celllines, className } = this.props;
    const { geneSelection, cellline } = this.state;
    let classes = "initialForm ";
    if (className) {
      classes += className;
    }
    return (
      <div className={classes}>
        <AutoComplete
          onSelect={this.selectCellline}
          deleteOnSelect={false}
          floatingLabelText="Cancer cellline"
          openOnFocus={true}
          dataSource={celllines}
        />
        <br />
        <RadioGroup
          className="radioButtonGroup"
          name="experimentType"
          value={this.state.experimentType}
          onChange={this._setExperimentType}
        >
          <FormControlLabel
            className="radioButton"
            value="knockout"
            control={<Radio />}
            label="Gene knockout"
          />
          <FormControlLabel
            className="radioButton"
            value="edit"
            control={<Radio />}
            label="Gene editing"
          />
        </RadioGroup>
        <AutoComplete
          floatingLabelText="Genes"
          deleteOnSelect={true}
          openOnFocus={true}
          dataSource={geneIds}
          onSelect={this.addGene}
        />
        <br />
        <div className="chipWrapper">
          {this.state.geneSelection.map((data: string) => {
            return this.renderChip(data);
          }, this)}
        </div>
        <Button
          onClick={() => this.props.go(geneSelection, cellline)}
          disabled={!geneSelection.length || !cellline}
          raised={true}
          className="formButton"
        >
          Go
        </Button>
      </div>
    );
  }
}
