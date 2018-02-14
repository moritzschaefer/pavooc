import * as React from "react";
import AutoComplete from "../util/AutoComplete";
import Radio, { RadioGroup } from "material-ui/Radio";
import { FormControlLabel } from "material-ui/Form";
import Button from "material-ui/Button";
import Chip from "material-ui/Chip";
import "./Form.css";
import CelllineSelector from "../util/CelllineSelector";
import { Gene } from "../IO/reducer";

export interface Props {
  goKnockout: (geneSelection: Array<string>) => {};
  goEdit: (geneId: string) => {};
  initialLoad: () => {};
  genes: Map<string, Gene>;
  className: string;
  onMessage: (message: string) => {};
}

export interface State {
  geneSelection: Map<string, string>;
  experimentType: string;
}

export default class Form extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
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
    const gene = genes.get(geneId);
    if (gene) {
      geneSelection.set(geneId, gene.geneSymbol);
    }
    this.setState({ geneSelection });
    return true;
  };

  _goButtonClick = () => {
    const { experimentType, geneSelection } = this.state;
    if (experimentType === "knockout") {
      this.props.goKnockout(Array.from(geneSelection.keys()));
    } else if (experimentType === "edit") {
      this.props.goEdit(Array.from(geneSelection.keys())[0]);

    }
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
    const { genes, className, onMessage } = this.props;
    const { geneSelection } = this.state;
    let classes = "initialForm ";
    if (className) {
      classes += className;
    }

    let reversedGenes = undefined;
    try {
      reversedGenes =
        genes &&
        new Map<string, string>(
          Array.from(genes.entries()).map(([key, value]: [string, Gene]): [string, string] => ([
            value.geneSymbol,
            key
          ]))
        );
    } catch (e) {}
    return (
      <div className={classes}>
        <CelllineSelector />
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
          onClick={this._goButtonClick}
          disabled={!geneSelection.size}
          raised={true}
          className="formButton"
        >
          Go
        </Button>
      </div>
    );
  }
}
