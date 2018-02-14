import * as React from "react";
import List, { ListItem, ListItemText } from "material-ui/List";
import Dialog, { DialogTitle } from "material-ui/Dialog";

interface State {
}

interface Props {
  data: Array<string>;
  selectIndex: (index: number) => void;
  opened: boolean;
}

export default class PdbSelectionDialog extends React.Component<Props, State> {
  render() {
    const { selectIndex, data, opened } = this.props;

    return (
      <Dialog open={opened} >
        <DialogTitle id="pdb-dialog-title">Choose PDB</DialogTitle>
        <div>
          <List>
            {data.map((pdb: string, index: number) => (
              <ListItem button={true} onClick={() => selectIndex(index)} key={index}>
                <ListItemText primary={pdb} />
              </ListItem>
            ))}
          </List>
        </div>
      </Dialog>
    );
  }
}
