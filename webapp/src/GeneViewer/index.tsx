import * as React from "react";
import { connect } from "react-redux";

import Button from "material-ui/Button";
import Input, { InputLabel } from "material-ui/Input";
import { MenuItem } from "material-ui/Menu";
import { FormControl } from "material-ui/Form";
import Select from "material-ui/Select";

import ProteinViewer from "./ProteinViewer";
import SequenceViewer from "./SequenceViewer";
import GuideTable from "./GuideTable";
import { setGuideCount } from "./actions";
import "./style.css";

interface Props {
  geneId: string;
  guideCount: number;
  setGuideCount: (event: any) => {};
}

interface State {}

class GeneViewer extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {};
  }
  render() {
    const { guideCount } = this.props;
    return (
      <div className="mainContainer">
        <div className="containerTop">
          <Button className="backButton">Back</Button>
          <h2 className="heading">Gene name</h2>
          <div className="topControls">
            <FormControl>
              <InputLabel htmlFor="guides-count">Guides per gene</InputLabel>
               <Select
                value={guideCount}
                onChange={this.props.setGuideCount}
                input={<Input id="guides-count" />}
                MenuProps={{
                              PaperProps: {
                                style: {
                                  maxHeight: 200
                                },
                              },
                            }}
              >
                {Array.from(new Array(10), (_: {}, i: number) => (
                  <MenuItem value={i} key={i}>
                    {i}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Button>&darr; CSV</Button>
          </div>
        </div>
        <div className="containerCenter">
          <ProteinViewer />
          <GuideTable />
        </div>
        <div className="containerBottom">
          <SequenceViewer />
        </div>
      </div>
    );
  }
}

const mapStateToProps = (
  state: any,
  { match: { params: { geneId } } }: { match: { params: { geneId: string } } }
) => ({
  guideCount: state.geneViewer.guideCount,
  geneId
});

const mapDispatchToProps = (dispatch: any) => ({
  setGuideCount: (event: any) => dispatch(setGuideCount(event.target.value))
});

export default connect(mapStateToProps, mapDispatchToProps)(GeneViewer);
