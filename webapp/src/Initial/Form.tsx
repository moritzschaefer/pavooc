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
  genes: Map<string, string>;
  celllines: Map<string, string>;
  className: string;
  onMessage: (message: string) => {};
}

export interface State {
  cellline: string;
  geneSelection: Map<string, string>;
  experimentType: string;
}

export default class Form extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      cellline: "UM-UC-3",
      experimentType: "knockout",
      geneSelection: new Map()
    };
  }
  componentDidMount() {
    this.props.initialLoad();
  }

  _setExperimentType = (event: any) => {
    this.setState({ experimentType: event.target.value });
  };

  addGene = (geneId: string) => {
    const { genes } = this.props;
    if (this.state.geneSelection.has(geneId)) {
      return false;
    }
    const geneSelection = new Map(this.state.geneSelection);
    const value = genes.get(geneId);
    if (value) {
      geneSelection.set(geneId, value);
    }
    this.setState({ geneSelection });
    return true;
  };

  selectCellline = (cellline: string): boolean => {
    this.setState({ cellline });
    return true;
  };

  removeGene = (geneId: string) => {
    const geneSelection = new Map(this.state.geneSelection);
    geneSelection.delete(geneId);
    this.setState({ geneSelection });
  };

  renderChip([geneId, geneSymbol]: [string, string]) {
    return (
      <Chip
        label={geneSymbol}
        key={geneId}
        onRequestDelete={() => this.removeGene(geneId)}
        className="geneChip"
      />
    );
  }

  render() {
    const { genes, celllines, className, onMessage } = this.props;
    const { geneSelection, cellline } = this.state;
    let classes = "initialForm ";
    if (className) {
      classes += className;
    }

    let reversedGenes = undefined;
    try {
      reversedGenes = genes && new Map(
        Array.from(genes.entries()).map(([key, value]): [
          string,
          string
        ] => [value, key])
      )

    } catch (e) {

    }
    return (
      <div className={classes}>
        <AutoComplete
          onSelect={this.selectCellline}
          deleteOnSelect={false}
          floatingLabelText="Cancer cellline"
          openOnFocus={true}
          dataSource={celllines}
          dataSourceReverse={undefined}
          onMessage={null}
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
          dataSource={genes}
          dataSourceReverse={reversedGenes}
          onSelect={this.addGene}
          onMessage={onMessage}
        />
        <br />
        <div className="chipWrapper">
          {Array.from(this.state.geneSelection.entries()).map(
            this.renderChip,
            this
          )}
        </div>
        <Button
          onClick={() =>
            this.props.go(Array.from(geneSelection.keys()), cellline)}
          disabled={!geneSelection.size || !cellline}
          raised={true}
          className="formButton"
        >
          Go
        </Button>
      </div>
    );
  }
}
