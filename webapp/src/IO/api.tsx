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
  }).then(handleFetchErrors)
    .then(response => response.json());
  return Observable.from(request);
};

export const fetchInitialApi = () => {
  const request = fetch(`/api/initial`, { method: "GET" })
  .then(handleFetchErrors)
  .then(response =>
    response.json()
  );
  return Observable.from(request);
};
