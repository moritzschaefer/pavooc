import { Observable } from "rxjs/Observable";

function handleFetchErrors(response: Response) {
  if (!response.ok) {
    throw Error(response.statusText);
  }
  return response;
}

export const fetchKnockoutsApi = (geneIds: any) => {
  const request = fetch(`/api/knockout`, {
    method: "POST",
    body: JSON.stringify({ gene_ids: geneIds })
  })
    .then(handleFetchErrors)
    .then(response => response.json());
  return Observable.from(request);
};

export const fetchInitialApi = () => {
  const request = fetch(`/api/initial`, { method: "GET" })
    .then(handleFetchErrors)
    .then(response => response.json())
    .then(response => {
      // TODO convert gene_id to geneId and
      let ret = response;
      ret.genes = ret.genes.map((g: any) => ({
        geneId: g.gene_id,
        geneSymbol: g.gene_symbol,
        start: g.start,
        end: g.end,
        chromosome: g.chromosome
      }));
      return ret;
    });
  return Observable.from(request);
};

export const fetchEditApi = (
  geneId: string,
  editPosition: number,
  padding: number = 400
) => {
  const request = fetch(`/api/edit`, {
    method: "POST",
    body: JSON.stringify({
      gene_id: geneId,
      edit_position: editPosition,
      padding: padding
    })
  })
    .then(handleFetchErrors)
    .then(response => response.json());
  return Observable.from(request);
};
