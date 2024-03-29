# SPDX-FileCopyrightText: 2024-present Pablo Collins <pcollins@splunk.com>
#
# SPDX-License-Identifier: MIT
import abc
from concurrent import futures

import grpc  # type: ignore
from opentelemetry.proto.collector.logs.v1 import logs_service_pb2, logs_service_pb2_grpc  # type: ignore
from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import ExportLogsServiceRequest  # type: ignore
from opentelemetry.proto.collector.metrics.v1 import metrics_service_pb2, metrics_service_pb2_grpc  # type: ignore
from opentelemetry.proto.collector.metrics.v1.metrics_service_pb2 import ExportMetricsServiceRequest  # type: ignore
from opentelemetry.proto.collector.trace.v1 import trace_service_pb2, trace_service_pb2_grpc  # type: ignore
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest  # type: ignore


class OtlpRequestHandlerABC(abc.ABC):

    @abc.abstractmethod
    def handle_logs(self, request: ExportLogsServiceRequest, context):
        pass

    @abc.abstractmethod
    def handle_metrics(self, request: ExportMetricsServiceRequest, context):
        pass

    @abc.abstractmethod
    def handle_trace(self, request: ExportTraceServiceRequest, context):
        pass


class OtlpGrpcServer:

    def __init__(self, request_handler: OtlpRequestHandlerABC):
        self._request_handler = request_handler
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        trace_service_pb2_grpc.add_TraceServiceServicer_to_server(
            TraceServiceServicer(request_handler.handle_trace), server
        )
        metrics_service_pb2_grpc.add_MetricsServiceServicer_to_server(
            MetricsServiceServicer(request_handler.handle_metrics), server
        )
        logs_service_pb2_grpc.add_LogsServiceServicer_to_server(
            LogsServiceServicer(request_handler.handle_logs), server
        )
        server.add_insecure_port("0.0.0.0:4317")
        self.server = server

    def start(self):
        """Starts the server. Does not block."""
        self.server.start()

    def wait_for_termination(self):
        """Blocks until the server stops"""
        self.server.wait_for_termination()

    def stop(self):
        self.server.stop(grace=None)


class LogsServiceServicer(logs_service_pb2_grpc.LogsServiceServicer):

    def __init__(self, handle_request):
        self.handle_request = handle_request

    def Export(self, request, context):  # noqa: N802
        self.handle_request(request, context)
        return logs_service_pb2.ExportLogsServiceResponse()


class TraceServiceServicer(trace_service_pb2_grpc.TraceServiceServicer):

    def __init__(self, handle_request):
        self.handle_request = handle_request

    def Export(self, request, context):  # noqa: N802
        self.handle_request(request, context)
        return trace_service_pb2.ExportTraceServiceResponse()


class MetricsServiceServicer(metrics_service_pb2_grpc.MetricsServiceServicer):

    def __init__(self, handle_request):
        self.handle_request = handle_request

    def Export(self, request, context):  # noqa: N802
        self.handle_request(request, context)
        return metrics_service_pb2.ExportMetricsServiceResponse()


class PrintHandler(OtlpRequestHandlerABC):

    def handle_logs(self, request, context):  # noqa: ARG002
        print(f"log request: {request}")  # noqa: T201

    def handle_metrics(self, request, context):  # noqa: ARG002
        print(f"metrics request: {request}")  # noqa: T201

    def handle_trace(self, request: ExportTraceServiceRequest, context):  # noqa: ARG002
        print(f"trace request: {request}")  # noqa: T201
