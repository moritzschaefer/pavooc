import * as React from "react";
import List, { ListItem, ListItemText } from "material-ui/List";
import Dialog, { DialogTitle } from "material-ui/Dialog";
import Button from "material-ui/Button";

interface State {
}

interface Props {
  selectIndex: (index?: number) => void;
  data: Array<string>;
  opened: boolean;
}

export default class PdbSelectionDialog extends React.Component<Props, State> {
  render() {
    const { data, selectIndex, opened } = this.props;

    return (
      <Dialog open={opened} >

        <DialogTitle id="pdb-dialog-title">Choose PDB</DialogTitle>
        <div>
          <List style={{ overflowY: "auto", maxHeight: 400 }}>
            {data.map((pdb: string, index: number) => (
              <ListItem button={true} onClick={() => selectIndex(index)} key={index}>
                <ListItemText primary={pdb} />
              </ListItem>
            ))}
          </List>
          <Button onClick={() => selectIndex()} style={{ margin: 10, float: "right" }}>
            Cancel
          </Button>
        </div>
      </Dialog>
    );
  }
}
