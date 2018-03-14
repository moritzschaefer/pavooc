import * as React from "react";
import Dialog, { DialogTitle } from "material-ui/Dialog";
import Button from "material-ui/Button";
import TextField from "material-ui/TextField";
import { codonToAA } from "../util/functions";

interface State {
  value: string;
}

export interface Props {
  originalCodon: string;
  editedCodon: string;
  position: number;
  setEditedCodon: (position: number, codon: string) => void;
  strand: string;
  onClose: () => void;
  opened: boolean;
}


export default class CodonEditDialog extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      value: ""
    };
  }

  componentDidMount() {
    this.setState({ value: this.props.editedCodon });
  }

  componentDidUpdate(prevProps: Props, prevState: State) {
    if (prevProps.editedCodon !== this.props.editedCodon) {
      this.setState({ value: this.props.editedCodon });
    }
  }

  _setEditedCodon = (event: any) => {
    const { value } = event.target;
    const { setEditedCodon, position } = this.props;
    if (value.length === 3 && value.match(/^[ACTGactg]+$/g) !== null) {
      setEditedCodon(position, value.toUpperCase()); // this will also edit state in componentDidUpdate
    }
    if (value.length <= 3) {
      this.setState({ value });
    }
  }
  render() {
    const { originalCodon, onClose, opened, strand } = this.props;
    const { value } = this.state;
    let originalAA = codonToAA(originalCodon, strand);
    let editedAA = codonToAA(value, strand);

    return (
      <Dialog open={opened} >

        <DialogTitle id="pdb-dialog-title">Edit codon</DialogTitle>
        <div style={{ padding: 25, paddingTop: 0 }}>
            <TextField
            id="with-placeholder"
            label={`Original: ${originalCodon}: ${originalAA}`}
            placeholder={originalCodon}
            style={{ display: "block" }}
            value={value}
            onChange={this._setEditedCodon}
            margin="normal"
          />
          <div>Edited AA: {editedAA}</div>
          <Button onClick={onClose} style={{ margin: 10, float: "right" }}>
            Close
          </Button>
        </div>
      </Dialog>
    );
  }
}
