
export async function putRequest(
    url: string,
    params: { [key: string]: any },
) {
    const rsp = await fetch(url, {
        body: JSON.stringify(params),
        headers: {
            "content-type": "application/json",
        },
        method: "PUT"
    });

    const text = await rsp.text();

    if (!rsp.ok) {
        throw Error(text);
    }

    try {
        console.log(JSON.parse(text));
        return JSON.parse(text);
    } catch (e) {
        return text;
    }
}

