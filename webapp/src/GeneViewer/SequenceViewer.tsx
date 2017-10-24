import * as React from "react";
// import * as pileup from "pileup";
import * as dalliance from "dalliance";

interface State {
  genome: string;
  genes: string;
}

interface Props {}

let viewport: HTMLDivElement | undefined = undefined;

export default class SequenceViewer extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);

    this.state = {
      genes: "http://www.derkholm.net:8080/das/hsa_54_36p/",
      genome: "http://www.derkholm.net:8080/das/hg18comp/"
    };
  }
  componentDidMount() {
    new dalliance.Browser({
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
          name: "Genes",
          desc: "Gene structures from GENCODE 19",
          bwgURI: "//www.biodalliance.org/datasets/gencode.bb",
          stylesheet_uri: "//www.biodalliance.org/stylesheets/gencode.xml",
          collapseSuperGroups: true,
          trixURI: "//www.biodalliance.org/datasets/geneIndex.ix"
        },
        {
          name: "Repeats",
          desc: "Repeat annotation from Ensembl",
          bwgURI: "//www.biodalliance.org/datasets/repeats.bb",
          stylesheet_uri: "//www.biodalliance.org/stylesheets/bb-repeats.xml"
        },
        {
          name: "Conservation",
          desc: "Conservation",
          bwgURI: "//www.biodalliance.org/datasets/phastCons46way.bw",
          noDownsample: true
        }
      ]
    });
  }
  // componentDidMount() {
  //   pileup.create(viewport, {
  //     range: { contig: "chr17", start: 7512384, stop: 7512544 },
  //     tracks: [
  //       {
  //         viz: pileup.viz.genome(),
  //         isReference: true,
  //         data: pileup.formats.twoBit({
  //           url: "http://www.biodalliance.org/datasets/hg19.2bit"
  //         }),
  //         name: "Reference"
  //       },
  //       {
  //         viz: pileup.viz.pileup(),
  //         data: pileup.formats.bigBed({
  //           url: "/exome.bed"
  //         }),
  //         cssClass: "normal",
  //         name: "Exons"
  //       }
  //       // ...
  //     ]
  //   });
  //
  // }
  render() {
    return <div id="svgHolder" ref={(ref: HTMLDivElement) => (viewport = ref)} />;
  }
}
