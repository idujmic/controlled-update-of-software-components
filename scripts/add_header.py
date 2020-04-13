from mitmproxy import http


def response(flow: http.HTTPFlow) -> None:
    flow.response.headers["newheader"] = "foo"
    f = open('out.txt', 'w')
    f.write(str(flow.response.headers) + '\n' + str(flow.response.body) + '\n')
    f.close()
