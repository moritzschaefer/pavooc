import * as React from "react";
import { connect } from "react-redux";
import { push } from "react-router-redux";

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

export interface GeneData {
  gene_id: string;
  guides: Array<any>;
  pdbs: Array<any>;
}

interface Props {
  geneId: string;
  guideCount: number;
  setGuideCount: (event: any) => {};
  geneData: GeneData;
  push: (route: string) => {};
}

interface State {
  selectedPdb: number;
  hoveredGuide: number | undefined;
}

class GeneViewer extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { selectedPdb: 0, hoveredGuide: undefined };
  }

  setHoveredGuide = (hoveredGuide: number): void => {
    this.setState({ hoveredGuide });
  };

  showPdb = (clickedPdb: string): void => {
    const { geneData } = this.props;
    const selectedPdb = geneData.pdbs.findIndex(
      (pdb: any) => pdb.PDB === clickedPdb
    );
    if (selectedPdb >= 0) {
      this.setState({ selectedPdb });
    } else {
      console.log("Error: selected pdb doesnt exist in genedata");
    }
  };

  render() {
    const { guideCount, geneData, geneId } = this.props;
    const { selectedPdb, hoveredGuide } = this.state;
    return (
      <div className="mainContainer">
        <div className="containerTop">
          <div className="geneViewerHeader">
            <Button
              onClick={() => this.props.push("/knockout")}
              raised={true}
              className="backButton"
            >
              Back
            </Button>
          </div>
          <h2 className="heading">{geneId}</h2>
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
                    }
                  }
                }}
              >
                {Array.from(new Array(10), (_: {}, i: number) => (
                  <MenuItem value={i} key={i}>
                    {i}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Button raised={true}>&darr; CSV</Button>
          </div>
        </div>
        <div className="containerCenter">
          <ProteinViewer
            hoveredGuide={hoveredGuide}
            setHoveredGuide={this.setHoveredGuide}
            className="proteinViewer"
            guides={geneData.guides}
            pdb={geneData.pdbs[selectedPdb]}
          />
          <GuideTable
            hoveredGuide={hoveredGuide}
            setHoveredGuide={this.setHoveredGuide}
            guides={geneData.guides}
            className="guideTable"
          />
        </div>
        <div className="containerBottom">
          <SequenceViewer
            hoveredGuide={hoveredGuide}
            guides={geneData.guides}
            onGuideHovered={this.setHoveredGuide}
            onPdbClicked={this.showPdb}
            gene={geneData}
          />
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
  geneData: state.io.guides.find((v: any) => v.gene_id === geneId),
  geneId
});

const mapDispatchToProps = (dispatch: any) => ({
  setGuideCount: (event: any) => dispatch(setGuideCount(event.target.value)),
  push: (route: string) => dispatch(push(route))
});

export default connect(mapStateToProps, mapDispatchToProps)(GeneViewer);
