import * as React from "react";
import * as pileup from "pileup";

interface State {
  genome: string;
  genes: string;
  repeats: string;
  medip: string;
}

interface Props {
}

let viewport: any = undefined;

export default class SequenceViewer extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);

    this.state = {
      genes: "http://www.derkholm.net:8080/das/hsa_54_36p/",
      repeats: "http://www.derkholm.net:8080/das/hsa_54_36p/",
      medip: "http://www.derkholm.net:8080/das/medipseq_reads",
      genome: "http://www.derkholm.net:8080/das/hg18comp/"
    };

  }
  componentDidMount() {
    pileup.create(viewport, {
      range: { contig: "chr17", start: 7512384, stop: 7512544 },
      tracks: [
        {
          viz: pileup.viz.genome(),
          isReference: true,
          data: pileup.formats.twoBit({
            url: "http://www.biodalliance.org/datasets/hg19.2bit"
          }),
          name: "Reference"
        },
        {
          viz: pileup.viz.pileup(),
          data: pileup.formats.bam({
            url: "/test-data/synth3.normal.17.7500000-7515000.bam",
            indexUrl: "/test-data/synth3.normal.17.7500000-7515000.bam.bai"
          }),
          cssClass: "normal",
          name: "Something"
        }
        // ...
      ]
    });
  }
  render() {
    return <div ref={(ref: any) => viewport = ref}/>;
  }
}
