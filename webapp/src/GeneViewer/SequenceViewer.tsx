import * as React from "react";
import * as dalliance from "dalliance";

import { GeneData } from "./GeneViewer";

interface State {
  genome: string;
  genes: string;
  browser: typeof dalliance.Browser | undefined;
}

interface Props {
  cellline: string;
  gene: typeof GeneData;
  guides: Array<any>;
  hoveredGuide: number | undefined;
  onGuideHovered: (hoveredGuide: number) => void;
  pdb: string;
  onPdbClicked: () => void;
}

let viewport: HTMLDivElement | undefined = undefined;

export default class SequenceViewer extends React.Component<any, State> {
  constructor(props: Props) {
    super(props);

    this.state = {
      genes: "http://www.derkholm.net:8080/das/hsa_54_36p/",
      genome: "http://www.derkholm.net:8080/das/hg18comp/",
      browser: undefined
    };
  }

  _highlightGuide(guide: any, clear: boolean = false) {
    const { gene } = this.props;
    const { browser } = this.state;
    if (clear) {
      browser.clearHighlights();
    }
    try {
      let exonStart = gene.exons.find(
        (exon: any) => exon.exon_id === guide.exon_id
      ).start;
      browser.highlightRegion(
        gene.chromosome,
        1 + guide.start + exonStart,
        1 + guide.start + exonStart + 23
      );
    } catch (e) {
      console.log(e);
      console.log(`${gene.gene_id} had no exon with exon_id`);
    }
  }

  componentDidUpdate(prevProps: Props, prevState: State) {
    const { hoveredGuide, guides, cellline, pdb } = this.props;
    const { browser } = this.state;
    if (!browser) {
      console.log("Error: browser must not be undefined"); // TODO make this throw instead of log
      return;
    }
    if (prevProps.hoveredGuide !== hoveredGuide) {

      if (hoveredGuide) {
        this._highlightGuide(guides[hoveredGuide], true);
      } else {
        // highlight all selected guides
        guides.filter((guide: any) => guide.selected).forEach((guide: any) => {
          this._highlightGuide(guide);
        });
      }
    }

    if (prevProps.cellline !== cellline) {
      browser.removeTier(this.cnsConfig(prevProps.cellline));
      browser.removeTier(this.snpConfig(prevProps.cellline));

      browser.addTier(this.cnsConfig(cellline));
      browser.addTier(this.snpConfig(cellline));
    }
    if (prevProps.pdb !== pdb) {
      browser.removeTier(this.pdbConfig(prevProps.pdb));
      browser.addTier(this.pdbConfig(pdb));
    }
  }

  // TODO test if this works
  _test = (i: any, info: any) => {
    info._inhibitPopup = true;
 }

  pdbConfig(pdb: string) {
    return {
      name: "PDB",
      desc: "PDB mapped to gene coordinates",
      uri: `/pdbs/${pdb}.bed`,
      tier_type: "memstore",
      payload: "bed",
      noSourceFeatureInfo: true,
      //disableDefaultFeaturePopup: true, // TODO try maybe
      featureInfoPlugin: this._test,
      style: [
        {
          type: "default",
          style: {
            glyph: "ANCHORED_ARROW",
            LABEL: true,
            HEIGHT: "10",
            BGITEM: true,
            STROKECOLOR: "black",
            BUMP: true,
            FGCOLOR: "black"
          }
        }
      ],
      collapseSuperGroups: true
    };
  }

  cnsConfig(cellline: string) {
    return {
      name: `${cellline} CNSs`,
      desc: `copy number segmentation data for cellline ${cellline}`,
      bwgURI: `/celllines/${cellline}_cns.bb`,
      style: [
        {
          type: "default",
          style: {
            glyph: "ANCHORED_ARROW",
            LABEL: true,
            HEIGHT: "12",
            BGITEM: true,
            STROKECOLOR: "black",
            BUMP: true,
            FGCOLOR: "black"
          }
        }
      ],
      collapseSuperGroups: true
    };
  }

  snpConfig(cellline: string) {
    return {
      name: `${cellline} SNPs`,
      desc: `mutations for cellline ${cellline}`,
      bwgURI: `/celllines/${cellline}_mutations.bb`,
      style: [
        {
          type: "default",
          style: {
            glyph: "ANCHORED_ARROW",
            LABEL: true,
            HEIGHT: "12",
            BGITEM: true,
            STROKECOLOR: "black",
            BUMP: true,
            FGCOLOR: "black"
          }
        }
      ],
      collapseSuperGroups: true
    };
  }

  // TODO we can use trix to speed up the browser
  componentDidMount() {
    const { gene, onPdbClicked, onGuideHovered, cellline, pdb } = this.props;

    let geneStart = Math.min(...gene.exons.map((exon: any) => exon.start));
    let geneEnd = Math.max(...gene.exons.map((exon: any) => exon.end));
    let chr = gene.chromosome;

    let browser = new dalliance.Browser({
      chr: chr,
      viewStart: geneStart,
      viewEnd: geneEnd,
      defaultSubtierMax: 3,

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
        this.cnsConfig(cellline),
        this.snpConfig(cellline),
        this.pdbConfig(pdb),
        {
          name: "Guides",
          desc: "sgRNAs in the exome",
          bwgURI: "/guides.bb",
          style: [
            {
              type: "default",
              style: {
                glyph: "ANCHORED_ARROW",
                LABEL: false,
                HEIGHT: "12",
                BGITEM: true,
                BUMP: true,
                STROKECOLOR: "black",
                FGCOLOR: "black",
                BGCOLOR: "blue"
              }
            }
          ],
          collapseSuperGroups: true
        },
        {
          name: "Genes",
          // style: [
          //   {
          //     type: "default",
          //     style: {
          //       glyph: "ARROW",
          //       LABEL: true,
          //       HEIGHT: "12",
          //       BGITEM: true,
          //       STROKECOLOR: "black",
          //       FGCOLOR: "black"
          //     }
          //   }
          // ],
          desc: "Gene structures from GENCODE 19",
          bwgURI: "/exome.bb",
          stylesheet_uri: "/gencode.xml",
          collapseSuperGroups: true
        }
      ]
    });
    browser.addFeatureHoverListener(
      (event: any, feature: any, hit: any, tier: any) => {
        if (tier.dasSource.name === "Guides") {
          const index = hit[0].id.split(":")[0] - 1;
          onGuideHovered(index);
        }
      }
    );
    browser.addFeatureListener(
      (event: any, feature: any, hit: any, tier: any) => {
        if (tier.dasSource.name === "PDB") {
          // delete current track, add new one
          onPdbClicked();
        }
      }
    );
    browser.addInitListener(() => browser.setLocation(chr, geneStart, geneEnd));
    this.setState({ browser });
  }

  render() {
    return (
      <div id="svgHolder" ref={(ref: HTMLDivElement) => (viewport = ref)} />
    );
  }
}
