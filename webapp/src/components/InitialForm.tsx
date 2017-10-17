import * as React from 'react';
import AutoComplete from './AutoComplete';
import Radio, { RadioGroup } from 'material-ui/Radio';
import { FormControlLabel } from 'material-ui/Form';
import { push } from 'react-router-redux'
import Button from 'material-ui/Button';
import Chip from 'material-ui/Chip';
import './InitialForm.css';

export interface Props {
  geneIds: Array<string>;
  celllines: Array<string>;
  className: string;
}

interface State {
  geneSelection: Array<string>;
  experimentType: string;
}

export default class InitialForm extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      experimentType: 'knockout',
      geneSelection: [
        'ENS1',
        'ENS2',
        'ENS3',
        'ENS5',
        'ENS9',
    ]};
  }

  _buttonClick = () => {
    // Show waiting spinner
    push('/knockout')
  }

  _setExperimentType = (event: any) => {
    this.setState({ experimentType: event.target.value });
  }

  addGene = (gene: string) => {
    if(this.state.geneSelection.find(v => v === gene)) {
      return false;
    }
    const geneSelection = [...this.state.geneSelection];
    geneSelection.push(gene);
    this.setState({geneSelection: geneSelection});
    return true;
  }

  removeGene = (data: string) => {
    const geneSelection = [...this.state.geneSelection];
    const chipToDelete = geneSelection.indexOf(data);
    geneSelection.splice(chipToDelete, 1);
    this.setState({ geneSelection });
  }

  renderChip(data: string) {
    return (
      <Chip
        label={data}
        key={data}
        onRequestDelete={this.removeGene}
        className="geneChip"
      />);
  }

  render() {
    const { geneIds, celllines, className } = this.props;
    let classes = 'initialForm ';
    if (className) {
      classes += className;
    }
    return (
      <div className={classes}>
        <AutoComplete
          onSelect={undefined}
          floatingLabelText="Cancer cellline"
          openOnFocus={true}
          dataSource={celllines}
        /><br />
        <RadioGroup
          className="radioButtonGroup"
          name="experimentType"
          value={this.state.experimentType}
          onChange={this._setExperimentType}
        >
            <FormControlLabel className="radioButton" value="knockout" control={<Radio />} label="Gene knockout" />
            <FormControlLabel className="radioButton" value="edit" control={<Radio />} label="Gene editing" />
        </RadioGroup>
        <AutoComplete
          floatingLabelText="Genes"
          openOnFocus={true}
          dataSource={geneIds}
          onSelect={this.addGene}
        /><br />
        <div className="chipWrapper">
          {this.state.geneSelection.map(
            (data: string) => {
              return this.renderChip(data);
            },
            this)
          }
        </div>
        <Button onClick={this._buttonClick} raised={true} className="formButton">Go</Button>
      </div>
    );
  }
}
