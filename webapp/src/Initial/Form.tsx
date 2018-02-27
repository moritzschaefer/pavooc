import * as React from "react";
import AutoComplete from "../util/AutoComplete";
import Radio, { RadioGroup } from "material-ui/Radio";
import { FormControlLabel } from "material-ui/Form";
import Button from "material-ui/Button";
import Chip from "material-ui/Chip";
import "./Form.css";
import CelllineSelector from "../util/CelllineSelector";

export interface Props {
  goKnockout: (geneSelection: Array<string>) => {};
  goEdit: (geneId: string) => {};
  initialLoad: () => {};
  genes: Map<string, string>;
  className: string;
  onMessage: (message: string) => {};
}

export interface State {
  geneSelection: Map<string, string>;
  editGene: [string, string];
  experimentType: string;
}

export default class Form extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      editGene: ["", ""],
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
    const { experimentType } = this.state;
    const { genes } = this.props;
    if (this.state.geneSelection.has(geneId)) {
      return false;
    }
    const geneSymbol = genes.get(geneId);

    if (geneSymbol) {
      if (experimentType === "knockout") {
        const geneSelection = new Map(this.state.geneSelection);
        geneSelection.set(geneId, geneSymbol);
        this.setState({ geneSelection });
      } else {
        this.setState({ editGene: [geneId, geneSymbol] });
      }
    }
    return true; // TODO this return might be wrong...
  };

  _goButtonClick = () => {
    const { experimentType, geneSelection, editGene } = this.state;
    if (experimentType === "knockout") {
      this.props.goKnockout(Array.from(geneSelection.keys()));
    } else if (experimentType === "edit") {
      this.props.goEdit(editGene[0]);
    }
  };

  removeGene = (geneId: string) => {
    const { experimentType } = this.state;
    if (experimentType === "knockout") {
      const geneSelection = new Map(this.state.geneSelection);
      geneSelection.delete(geneId);
      this.setState({ geneSelection });
    } else {
      this.setState({ editGene: ["", ""] });
    }
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
    const { geneSelection, experimentType, editGene } = this.state;
    let classes = "initialForm ";
    if (className) {
      classes += className;
    }

    let reversedGenes = undefined;
    try {
      reversedGenes =
        genes &&
        new Map<string, string>(
          Array.from(genes.entries()).map(([key, value]: [string, string]): [
            string,
            string
          ] => [value, key])
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
          {experimentType === "knockout"
            ? Array.from(this.state.geneSelection.entries()).map(
                this.renderChip,
                this
              )
            : editGene[0] !== "" ? this.renderChip(editGene) : null}
        </div>
        <Button
          onClick={this._goButtonClick}
          disabled={
            (experimentType === "knockout" && !geneSelection.size) ||
            (experimentType === "edit" && editGene[0] === "")
          }
          raised={true}
          className="formButton"
        >
          Go
        </Button>
      </div>
    );
  }
}
