from otelserver import OtlpGrpcServer, PrintHandler


def test_server():
    svr = OtlpGrpcServer(PrintHandler())
    svr.start()
    svr.stop()
