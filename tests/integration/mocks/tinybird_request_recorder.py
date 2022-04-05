from io import BytesIO


class WSGIRecordData:
    def __init__(self, application):
        self.application = application
        self.recorded_copy = []

    def __call__(self, environ, start_response):
        length = int(environ.get("CONTENT_LENGTH") or 0)
        if length:
            body = environ["wsgi.input"].read(length)
            record = {
                "raw-uri": environ["RAW_URI"],
                "request-method": environ["REQUEST_METHOD"],
                "http-authorization": environ["HTTP_AUTHORIZATION"],
                "data": body,
            }
            print(record)
            self.recorded_copy.append(record)
            # replace the stream since it was exhausted by read()
            environ["wsgi.input"] = BytesIO(body)
        return self.application(environ, start_response)

    def get_recorded_requests(self):
        return self.recorded_copy


if __name__ == "__main__":
    from flask import request
    from http_server_mock import HttpServerMock

    app = HttpServerMock(__name__)
    port = 5111
    host = "0.0.0.0"
    tinybird_mock_path = "/tinybird"
    tinybird_mock_url = f"http://{host}:{port}{tinybird_mock_path}"

    @app.route(tinybird_mock_path, methods=["POST"])
    def index():
        print(request.data)
        return "success"

    print(f"starting app on {host}:{port}")
    app.run(host, port)
