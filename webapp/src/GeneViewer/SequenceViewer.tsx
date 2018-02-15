import * as React from "react";
import * as dalliance from "dalliance";

interface State {
  genome: string;
  genes: string;
  viewStart: number;
  viewEnd: number;
  viewChromosome: string;
  browser: typeof dalliance.Browser | undefined;
}

interface Props {
  cellline: string;
  chromosome: string;
  geneStart: number;
  geneEnd: number;
  exons: Array<any> | undefined;
  guides: Array<any>;
  hoveredGuide: number | undefined;
  onGuideHovered: (hoveredGuide: number | undefined) => void;
  pdb: string | undefined;
  editPosition: number;
  editPositionChanged: ((editPosition: number) => void) | undefined;
  onPdbClicked: () => void;
  onNucleotideClick?: (nucleotidePosition: number) => void;
}

let viewport: HTMLDivElement | undefined = undefined;

export default class SequenceViewer extends React.Component<any, State> {
  constructor(props: Props) {
    super(props);

    this.state = {
      genes: "http://www.derkholm.net:8080/das/hsa_54_36p/",
      genome: "http://www.derkholm.net:8080/das/hg18comp/",
      viewStart: -1,
      viewEnd: -1,
      viewChromosome: "",
      browser: undefined
    };
  }

  _highlightGuide(guide: any, clear: boolean = false) {
    const { exons, chromosome } = this.props;
    const { browser } = this.state;
    if (clear) {
      browser.clearHighlights();
    }
    try {
      let exonStart = exons.find((exon: any) => exon.exon_id === guide.exon_id)
        .start;
      browser.highlightRegion(
        chromosome,
        1 + guide.start + exonStart,
        1 + guide.start + exonStart + 23
      );
    } catch (e) {
      console.log(e);
    }
  }

  componentDidUpdate(prevProps: Props, prevState: State) {
    const { hoveredGuide, guides, cellline, pdb, editPosition } = this.props;
    const { browser, viewStart } = this.state;
    if (!browser) {
      console.log("Error: browser must not be undefined"); // TODO make this throw instead of log
      return;
    }
    if (prevProps.hoveredGuide !== hoveredGuide) {
      if (guides[hoveredGuide]) {
        this._highlightGuide(guides[hoveredGuide], true);
      } else {
        browser.clearHighlights();
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
      if (prevProps.pdb) {
        browser.removeTier(this.pdbConfig(prevProps.pdb));
      }
      if (pdb) {
        browser.addTier(this.pdbConfig(pdb));
      }
    }
    if (
      prevProps.editPosition !== editPosition ||
      prevState.viewStart !== viewStart
    ) {
      this._drawEditPosition();
    }
  }

  // TODO test if this works
  _test = (i: any, info: any) => {
    info._inhibitPopup = true;
  };

  pdbConfig(pdb: string) {
    return {
      name: "PDB",
      desc: "PDB mapped to gene coordinates",
      uri: `/pdbs/${pdb}.bed`,
      tier_type: "memstore",
      payload: "bed",
      noSourceFeatureInfo: true,
      disableDefaultFeaturePopup: true, // TODO try maybe
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

  // Draw the editposition marker right into the dalliance
  _drawEditPosition() {
    const { viewStart /*, viewEnd, viewChromosome*/ } = this.state;
    const { editPosition } = this.props;
    if (!editPosition || viewStart < 0) {
      return;
    }

    // TODO find perfect position and draw!
  }
  _initialSources() {
    const { pdb, cellline } = this.props;
    let sources: Array<any> = [
      {
        name: "Genome",
        twoBitURI: "//www.biodalliance.org/datasets/hg19.2bit",
        tier_type: "sequence"
      },
      this.cnsConfig(cellline),
      this.snpConfig(cellline),
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
    ];
    if (pdb) {
      sources.push(this.pdbConfig(pdb));
    }
    return sources;
  }

  // TODO we can use trix to speed up the browser
  componentDidMount() {
    let { // const
      chromosome,
      geneStart,
      geneEnd,
      onPdbClicked,
      onGuideHovered,
      editPositionChanged
    } = this.props;

    let chr = chromosome;
    if (!chr) { // TODO workaround delete
      chr = "chr22";
      geneStart = 40000000;
      geneEnd = 40000600;
    }

    let browser = new dalliance.Browser({
      chr,
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
      sources: this._initialSources()
    });
    browser.addFeatureHoverListener(
      (event: any, feature: any, hit: any, tier: any) => {
        if (tier.dasSource.name === "Guides") {
          // const index = hit[0].id.split(":")[0] - 1;
          if (feature) {
            const index = feature.label.split(":")[0] - 1;
            onGuideHovered(index);
          } else {
            onGuideHovered(undefined);
          }
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
    browser.addViewListener(
      (viewChromosome: string, viewStart: number, viewEnd: number) =>
        this.setState({ viewChromosome, viewStart, viewEnd })
    );
    browser.addInitListener(() => {
      browser.setLocation(chr, geneStart, geneEnd)

      if (editPositionChanged) {
        // TODO only for gene editing
        // // TODO add hovering
        // Tier 0 is the genome
        //
        browser.tiers[0].viewport.addEventListener("click", this._genomeClick);
      }
    });
    this.setState({ browser });
  }

  _genomeClick = (event: any) => {
    const { viewStart, viewEnd } = this.state;
    const { editPositionChanged } = this.props;
    const clickPosition = event.x;
    const browserWidth = event.target.parentElement.parentElement.offsetWidth;

    const nucleotidePosition = Math.floor(viewStart + (clickPosition / browserWidth) * (viewEnd - viewStart));
    editPositionChanged(nucleotidePosition);
  }

  render() {
    return (
      <div id="svgHolder" ref={(ref: HTMLDivElement) => (viewport = ref)} />
    );
  }
}
