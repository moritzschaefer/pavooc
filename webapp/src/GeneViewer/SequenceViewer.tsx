import * as React from "react";
import * as dalliance from "dalliance";
// import shallowCompare from "react-addons-shallow-compare";
import { codonToAA, arraysEqual } from "../util/functions";

export interface SeqEditData {
  start: number;
  sequence: string;
  strand: string;
  aaStart?: number;
}

interface State {
  // genome: string;
  // genes: string;
  viewStart: number;
  viewEnd: number;
  viewChromosome: string;
  browser: typeof dalliance.Browser | undefined;
}

interface Props {
  cellline: string;
  chromosome: string;
  cns?: Array<string>;
  geneStart: number;
  geneEnd: number;
  guidesUrl?: string;
  exons: Array<any> | undefined;
  guides: Array<any>;
  hoveredGuide: number | undefined;
  onGuideHovered: (hoveredGuide: number | undefined) => void;
  onGuideClicked: ((index: number) => void);
  onPdbClicked: () => void;
  editData?: SeqEditData;
  onEditCodonClicked?: (codon: number) => void;
}

const EDIT_CONFIG_NAME = "Edit Template";
let viewport: HTMLDivElement | undefined = undefined;

export default class SequenceViewer extends React.Component<any, State> {
  constructor(props: Props) {
    super(props);

    this.state = {
      // genes: "http://www.derkholm.net:8080/das/hsa_54_36p/",
      // genome: "http://www.derkholm.net:8080/das/hg18comp/",
      viewStart: -1,
      viewEnd: -1,
      viewChromosome: "",
      browser: undefined,
    };
  }

  _highlightGuide(guide: any, clear: boolean = false) {
    const { chromosome } = this.props;
    const { browser } = this.state;
    if (clear) {
      browser.clearHighlights();
    }
    let guideStart = guide.start + 1;
    browser.highlightRegion(chromosome, guideStart, guideStart + 23);
  }

  componentDidUpdate(prevProps: Props, prevState: State) {
    const { hoveredGuide, guides, cellline, guidesUrl, editData } = this.props;
    const { browser } = this.state;
    if (!browser) {
      console.log("Error: browser must not be undefined"); // TODO make this throw instead of log
      return;
    }
    if (
      prevProps.hoveredGuide !== hoveredGuide ||
      !arraysEqual(
        guides.map((guide: any) => guide.selected),
        prevProps.guides.map((guide: any) => guide.selected)
      )
    ) {
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

    if (
      (typeof prevProps.editData === "undefined") !==
        (typeof editData === "undefined") ||
      (prevProps.editData &&
        editData &&
        prevProps.editData.sequence !== editData.sequence)
    ) {
      // TODO this will NOT track change of object keys/values
      let oldEdit = this.editConfig(prevProps.editData);
      let newEdit = this.editConfig(editData);
      if (oldEdit) {
        // the source is local, which is why removeTier can't find the correct tier without help
        oldEdit.index = browser.tiers.findIndex(
          (tier: any) => tier.dasSource.name === EDIT_CONFIG_NAME
        );
        // delete prevprops.editData
        browser.removeTier(oldEdit);
      }
      if (newEdit) {
        browser.addTier(newEdit);
      }
    }

    if (prevProps.cellline !== cellline || prevProps.guidesUrl !== guidesUrl) {
      let oldCns = this.cnsConfig(prevProps.cellline);
      let oldSnp = this.snpConfig(prevProps.cellline);

      let newCns = this.cnsConfig(cellline);
      let newSnp = this.snpConfig(cellline);

      if (oldCns) {
        browser.removeTier(oldCns);
      }
      if (oldSnp) {
        browser.removeTier(oldCns);
      }

      if (newCns) {
        browser.addTier(newCns);
      }
      if (newSnp) {
        browser.addTier(newSnp);
      }
    }

    if (prevProps.guidesUrl !== guidesUrl) {
      browser.removeTier(this.guidesConfig(prevProps.guidesUrl));
      browser.addTier(this.guidesConfig(guidesUrl));
    }

    // TODO improve check on this one!
  }

  // TODO test if this works
  _test = (i: any, info: any) => {
    info._inhibitPopup = true;
  };

  editConfig(editData: SeqEditData | undefined) {
    const { chromosome } = this.props;
    if (editData && editData.sequence !== "") {
      const features = [];
      // chrX	99885797	99891691	ENSG00000000003.10	0	-	99885797	99891691	255,0,0
      for (var i = 0, len = editData.sequence.length; i < len; i += 3) {
        let aa = codonToAA(editData.sequence.slice(i, i + 3), editData.strand);

        features.push(
          `${chromosome.slice(3, 5)} ${editData.start + i} ${editData.start +
            i +
            3} ${aa}`
        );
      }
      return {
        index: undefined,
        name: EDIT_CONFIG_NAME,
        tier_type: "memstore",
        type: "codon",
        payload: "bed",
        uri: URL.createObjectURL(new Blob([features.join("\n")]))
      };
    } else {
      return undefined;
    }
  }

  cnsConfig(cellline: string) {
    const { cns } = this.props;
    // only show BED if it exists
    if (!cns || !cns.includes(cellline)) {
      return undefined;
    }
    return {
      name: `${cellline} CNSs`,
      desc: `copy number segmentation data for cellline ${cellline}`,
      uri: `/celllines/${cellline}_cns.bed`,
      tier_type: "memstore",
      payload: "bed",
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
    const { guides } = this.props;
    // only show BED if it exists
    if (!guides.find((g: any) => g.mutations.includes(cellline))) {
      return undefined;
    }
    return {
      name: `${cellline} SNPs`,
      desc: `mutations for cellline ${cellline}`,
      uri: `/celllines/${cellline}_mutations.bed`,
      tier_type: "memstore",
      payload: "bed",
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

  guidesConfig(url: string = "") {
    // if url is undefined we load the complete guide file
    if (!url) {
      return {
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
      };
    } else {
      // else we load the provided url
      return {
        name: "Guides",
        desc: "sgRNAs for the provided edit position",
        uri: url,
        tier_type: "memstore",
        payload: "bed",
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
        ]
      };
    }
  }

  _initialSources() {
    const { cellline, guidesUrl, editData } = this.props;
    let genomeURI = "//www.biodalliance.org/datasets/hg19.2bit";

    let sources: Array<any> = [
      {
        name: "Genome",
        twoBitURI: genomeURI,
        tier_type: "sequence"
      },
      {
        name: "Canonical transcripts",
        bwgURI: "/exome.bb",
        tier_type: "translation",
        subtierMax: 1,
        // stylesheet_uri: "/gencode.xml",
        style: [
          {
            type: "translation",
            style: {
              ZINDEX: 5,
              glyph: "BOX",
              LABEL: true,
              HEIGHT: "12",
              BGITEM: true,
              STROKECOLOR: "green",
              FGCOLOR: "black",
              BUMP: false
            }
          }
        ],
        collapseSuperGroups: false
      },
      this.guidesConfig(guidesUrl),
      //{
      //name: "Genes", // TODO we just use this to show the direction of the gene
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
      // desc: "Gene structures from GENCODE 19",
      // bwgURI: "/exome.bb",
      // stylesheet_uri: "/gencode.xml",
      // collapseSuperGroups: true
      // },
      {
        name: "Domains",
        desc: "Domains mapped to gene coordinates",
        bwgURI: "/domains.bb",
        noSourceFeatureInfo: true,
        disableDefaultFeaturePopup: true,
        featureInfoPlugin: this._test,
        subtierMax: 2,
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
      },
      {
        name: "PDB",
        desc: "PDBs mapped to gene coordinates",
        bwgURI: "/pdbs.bb",
        noSourceFeatureInfo: true,
        disableDefaultFeaturePopup: true,
        featureInfoPlugin: this._test,
        subtierMax: 2,
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
      }
    ];

    let cnsConfig = this.cnsConfig(cellline);
    if (cnsConfig) {
      sources.push(cnsConfig);
    }

    let snpConfig = this.snpConfig(cellline);
    if (snpConfig) {
      sources.push(snpConfig);
    }
    let editConfig = this.editConfig(editData);
    if (editConfig) {
      sources.push(editConfig);
    }

    return sources;
  }

  _loadBrowser = () => {
    let {
      // const
      chromosome,
      geneStart,
      geneEnd,
      onPdbClicked,
      onGuideHovered,
      onEditCodonClicked,
      onGuideClicked
    } = this.props;
    let chr = chromosome;
    const padding = Math.floor((geneEnd - geneStart) / 7);
    let browser = new dalliance.Browser({
      chr,
      viewStart: geneStart - padding,
      viewEnd: geneEnd + padding,
      defaultSubtierMax: 3,
      disablePoweredBy: true,

      coordSystem: {
        speciesName: "Human",
        taxon: 9606,
        auth: "GRCh",
        version: "37",
        ucscName: "hg19"
      },
      sources: this._initialSources()
    });
    // workaround: Dalliance automatically adds locally stored sources..
    let editSource = browser.sources.findIndex((source: any) => source.name === EDIT_CONFIG_NAME);
    if (typeof editSource !== "undefined" ) {
      browser.sources.splice(editSource, 1);
    }
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
      },
      { immediate: true }
    );
    browser.addFeatureListener(
      (event: any, feature: any, hit: any, tier: any) => {
        if (tier.dasSource.name === "PDB") {
          onPdbClicked();
        }
        if (tier.dasSource.name === EDIT_CONFIG_NAME && onEditCodonClicked) {
          onEditCodonClicked(feature.min - 1); // make 0-based
        }
        if (tier.dasSource.name === "Guides" && feature) {
          const index = feature.label.split(":")[0] - 1;
          onGuideClicked(index);
        }
      }
    );
    browser.addViewListener(
      (viewChromosome: string, viewStart: number, viewEnd: number) => {
        if (
          this.state.viewChromosome !== viewChromosome ||
          this.state.viewStart !== viewStart ||
          this.state.viewEnd !== viewEnd
        ) {
          this.setState({
            viewChromosome,
            viewStart,
            viewEnd
          });
        }
      }
    );
    browser.addInitListener(() => {
      browser.setLocation(chr, geneStart - padding, geneEnd + padding);
    });
    this.setState({ browser });
  };

  // TODO we can use trix to speed up the browser
  componentDidMount() {
    this._loadBrowser();
  }

  shouldComponentUpdate(nextProps: Props, nextState: State) {
    return true;
    // return shallowCompare(this, nextProps, nextState);
  }

  render() {
    return (
      <div id="svgHolder" ref={(ref: HTMLDivElement) => (viewport = ref)} />
    );
  }
}
