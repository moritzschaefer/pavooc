export const downloadCSV = (
  geneData: Array<any>,
  exportFilename: string,
  editData: {
        template: string;
        templateStart: number;
        originalSequence: string;
        editPositions: Array<number>;
      } | undefined = undefined
) => {
  // TODO orientation->guideOrientation, geneStrand
  const data = [].concat(
    // flatten array of arrays
    ...geneData.map((gene: any) =>
      gene.guides
        .filter((guide: any) => guide.selected) // only return selected guides
        .map((guide: any) => ({
          cns: gene.cns,
          chromosome: gene.chromosome,
          gene_id: gene.gene_id,
          exon_id: guide.exon_id,
          target: guide.target,
          on_target_score: guide.scores.azimuth, // TODO change to my score!
          off_target_score: guide.scores.Doench2016CFDScore,
          start: guide.start,
          cut_position: guide.cut_position,
          aa_cut_position: guide.aa_cut_position,
          otCount: guide.otCount,
          orientation: guide.orientation
        }))
    )
  );

  // add template to objects
  if (editData) {
    // TODO should be one only..
    data.forEach((obj: any) => {
      obj.template = editData.template;
      obj.templateStart = editData.templateStart;
      obj.originalSequence = editData.originalSequence;
      obj.editDistance = editData.editPositions
        .map((editPosition: number) => Math.abs(editPosition - obj.cut_position))
        .join("|");
    });
  }

  const columnDelimiter = ",";
  const lineDelimiter = "\n";

  let keys = Object.keys(data[0]);

  let result = "";
  result += keys.join(columnDelimiter);
  result += lineDelimiter;

  data.forEach(function(item: any) {
    let ctr = 0;
    keys.forEach(function(key: string) {
      if (ctr > 0) {
        result += columnDelimiter;
      }

      result += item[key];
      ctr++;
    });
    result += lineDelimiter;
  });
  // now generate a link
  var csvData = new Blob([result], { type: "text/csv;charset=utf-8;" });
  // IE11 & Edge
  if (navigator.msSaveBlob) {
    navigator.msSaveBlob(csvData, exportFilename);
  } else {
    // TODO In FF link must be added to DOM to be clicked
    var link = document.createElement("a");
    link.href = window.URL.createObjectURL(csvData);
    link.setAttribute("download", exportFilename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
};

export const arraysEqual = (a: Array<any>, b: Array<any>) => {
  // if the other array is a falsy value, return
  if (!a) {
    return false;
  }

  // compare lengths - can save a lot of time
  if (b.length !== a.length) {
    return false;
  }

  for (var i = 0, l = b.length; i < l; i++) {
    // Check if we have nested arrays
    if (b[i] instanceof Array && a[i] instanceof Array) {
      // recurse into the nested arrays
      if (!b[i].equals(a[i])) {
        return false;
      }
    } else if (b[i] !== a[i]) {
      // Warning - two different object instances will never be equal: {x:20} != {x:20}
      return false;
    }
  }
  return true;
};

interface Domain {
  start: number;
  end: number;
  name: string;
}

export const guidesWithDomains = (geneData: any) => {
  return geneData.guides.map((guide: any) => ({
    ...guide,
    domains: geneData.domains
      .filter(
        (domain: Domain) =>
          domain.start < guide.cut_position && domain.end > guide.cut_position
      )
      .map((domain: Domain) => domain.name)
  }));
};

export const reverseComplement = (sequence: string) => {
  const dict = new Map([["A", "T"], ["T", "A"], ["C", "G"], ["G", "C"]]);
  let outSeq = [];
  for (var c of sequence
    .toUpperCase()
    .split("")
    .reverse()) {
    outSeq.push(dict.get(c));
  }
  return outSeq.join("");
};

export const codonToAA = (codon: string, strand: string = "+") => {
  let processedCodon;
  if (strand === "+") {
    processedCodon = codon.toUpperCase();
  } else {
    processedCodon = reverseComplement(codon);
  }

  const threeLetterCodes = new Map([
    ["A", "ALA"],
    ["R", "ARG"],
    ["N", "ASN"],
    ["D", "ASP"],
    ["B", "ASX"],
    ["C", "CYS"],
    ["E", "GLU"],
    ["Q", "GLN"],
    ["Z", "GLX"],
    ["G", "GLY"],
    ["H", "HIS"],
    ["I", "ILE"],
    ["L", "LEU"],
    ["K", "LYS"],
    ["M", "MET"],
    ["F", "PHE"],
    ["P", "PRO"],
    ["S", "SER"],
    ["T", "THR"],
    ["W", "TRP"],
    ["Y", "TYR"],
    ["V", "VAL"]
  ]);
  const codonMap = new Map([
    ["A", ["GCA", "GCC", "GCG", "GCT"]],
    ["C", ["TGC", "TGT"]],
    ["D", ["GAC", "GAT"]],
    ["E", ["GAA", "GAG"]],
    ["F", ["TTC", "TTT"]],
    ["G", ["GGA", "GGC", "GGG", "GGT"]],
    ["H", ["CAC", "CAT"]],
    ["I", ["ATA", "ATC", "ATT"]],
    ["K", ["AAA", "AAG"]],
    ["L", ["CTA", "CTC", "CTG", "CTT", "TTA", "TTG"]],
    ["M", ["ATG"]],
    ["N", ["AAC", "AAT"]],
    ["P", ["CCA", "CCC", "CCG", "CCT"]],
    ["Q", ["CAA", "CAG"]],
    ["R", ["AGA", "AGG", "CGA", "CGC", "CGG", "CGT"]],
    ["S", ["AGC", "AGT", "TCA", "TCC", "TCG", "TCT"]],
    ["T", ["ACA", "ACC", "ACG", "ACT"]],
    ["V", ["GTA", "GTC", "GTG", "GTT"]],
    ["W", ["TGG"]],
    ["Y", ["TAC", "TAT"]]
  ]);
  const invertedMap = new Map();
  for (var [key, value] of Array.from(codonMap)) {
    for (var c of value) {
      invertedMap.set(c, key);
    }
  }
  try {
    return threeLetterCodes.get(invertedMap.get(processedCodon));
  } catch (e) {
    return "";
  }
};
