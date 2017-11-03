import * as React from "react";
import * as dalliance from "dalliance";

interface State {
  genome: string;
  genes: string;
  browser: typeof dalliance.Browser | undefined;
}

interface Props {}

let viewport: HTMLDivElement | undefined = undefined;

export default class SequenceViewer extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);

    this.state = {
      genes: "http://www.derkholm.net:8080/das/hsa_54_36p/",
      genome: "http://www.derkholm.net:8080/das/hg18comp/",
      browser: undefined
    };
  }

  // TODO we can use trix to speed up the browser

  componentDidMount() {
    let browser = new dalliance.Browser({
      chr: "22",
      viewStart: 30700000,
      viewEnd: 30900000,

      coordSystem: {
        speciesName: "Human",
        taxon: 9606,
        auth: "GRCh",
        version: "37",
        ucscName: "hg19"
      },

      sources: [
        {
          name: "Genome",
          twoBitURI: "//www.biodalliance.org/datasets/hg19.2bit",
          tier_type: "sequence"
        },
        {
          name: "PDBs",
          desc: "PDBs mapped to gene coordinates",
          bwgURI: "/sorted_pdbs.bb",
          stylesheet_uri: "//www.biodalliance.org/stylesheets/gencode.xml",
          collapseSuperGroups: true
        },
        {
          name: "Genes",
          desc: "Gene structures from GENCODE 19",
          bwgURI: "/exome.bb",
          stylesheet_uri: "//www.biodalliance.org/stylesheets/gencode.xml",
          collapseSuperGroups: true
        }
      ]
    });
    this.setState({ browser });
  }

  render() {
    return (
      <div id="svgHolder" ref={(ref: HTMLDivElement) => (viewport = ref)} />
    );
  }
}
