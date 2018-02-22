import { Observable } from "rxjs/Observable";

function handleFetchErrors(response: Response) {
  if (!response.ok) {
    throw Error(response.statusText);
  }
  return response;
}

export const fetchKnockoutsApi = (geneIds: any) => {
  const request = fetch("/api/knockout", {
    method: "POST",
    body: JSON.stringify({ gene_ids: geneIds })
  })
    .then(handleFetchErrors)
    .then(response => response.json());
  return Observable.from(request);
};

export const fetchInitialApi = () => {
  const request = fetch("/api/initial", { method: "GET" })
    .then(handleFetchErrors)
    .then(response => response.json())
    .then(response => {
      // TODO convert gene_id to geneId and
      response.genes = response.genes.map((g: any) => ({
        pdbs: g.pdbs,
        strand: g.strand,
        geneId: g.gene_id,
        geneSymbol: g.gene_symbol,
        start: g.start,
        end: g.end,
        chromosome: g.chromosome
      }));
      return response;
    });
  return Observable.from(request);
};

const renameAttribute = (obj: any, oldName: string, newName: string) => {
  Object.defineProperty(
    obj,
    newName,
    Object.getOwnPropertyDescriptor(
      obj,
      oldName
    ) as PropertyDescriptor
  );
  delete obj[oldName];
}

export const fetchEditApi = (
  geneId: string,
  editPosition: number,
  padding: number = 400
) => {
  const request = fetch("/api/edit", {
    method: "POST",
    body: JSON.stringify({
      gene_id: geneId,
      edit_position: editPosition,
      padding: padding
    })
  })
    .then(handleFetchErrors)
    .then(response => response.json())
    .then(res => {
      // TODO convert snake to camel case
      renameAttribute(res, "guides_after", "guidesAfter");
      renameAttribute(res, "guides_before", "guidesBefore");
      renameAttribute(res, "bed_url", "bedUrl");

      return res;
    });
  return Observable.from(request);
};
