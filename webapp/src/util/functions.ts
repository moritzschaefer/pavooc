export const downloadCSV = (geneData: Array<any>, exportFilename: string, template: string | undefined = undefined) => {
  // TODO orientation->guideOrientation, geneStrand
  const data = [].concat(
    // flatten array of arrays
    ...geneData.map((gene: any) =>
      gene.guides
        .filter((guide: any) => guide.selected) // only return selected guides
        .map((guide: any) => ({
            cns: gene.cns,
            gene_id: gene.gene_id,
            exon_id: guide.exon_id,
            target: guide.target,
            on_target_score: guide.scores.azimuth,  // TODO change to my score!
            off_target_score: guide.scores.Doench2016CFDScore,
            start: guide.start,
            cut_position: guide.cut_position,
            aa_cut_position: guide.aa_cut_position,
            otCount: guide.otCount,
            orientation: guide.orientation
          })
        )
    )
  );

  // add template to objects
  if (template) {
    data.forEach((obj: any) => {
      obj.template = template;
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
}
