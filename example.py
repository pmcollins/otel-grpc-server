from otelserver import OtlpGrpcServer, PrintHandler

svr = OtlpGrpcServer(PrintHandler())
svr.start()
print('hello')
svr.stop()

