interface PutRequestType {
    url: string;
    params: { [key: string]: any };
}

export async function putRequest(url: string, params: { [key: string]: any }) {
    const rsp = await fetch(url, {
        body: JSON.stringify(params),
        headers: {
            "content-type": "application/json",
        },
        method: "PUT",
    });

    const text = await rsp.text();

    if (!rsp.ok) {
        throw Error(text);
    }

    try {
        return JSON.parse(text);
    } catch (e) {
        return text;
    }
}

export async function chainPutRequests(...requests: PutRequestType[]) {
    let promises: Promise<any>[] = [];
    requests.forEach((r) => {
        promises.push(putRequest(r.url, r.params));
    });
    await Promise.all(promises);
}
