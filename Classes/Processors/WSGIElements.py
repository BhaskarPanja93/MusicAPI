from pathlib import Path
from flask import Flask
from gevent.pywsgi import WSGIHandler, WSGIServer

from customisedLogs import CustomisedLogs


class WSGIRunner:
    def __init__(self, app: Flask, port: int, route: str, logger: CustomisedLogs, cert_file=None, key_file=None):
        """
        Start the WSGI server with SSL errors suppressed and customised logs enabled
        :param app: app to serve
        :param port: port to serve on
        :param route: route to print
        :param logger: customisedLogger
        :param cert_file: ssl cert file
        :param key_file: ssl key file
        """
        if cert_file is not None and key_file is not None and Path(cert_file).is_file() and Path(key_file).is_file():
            print(f"https://127.0.0.1:{port}{route}")
            WSGIRunner.LogAttached(('0.0.0.0', port,), app, logger, certfile=cert_file, keyfile=key_file).serve_forever()
        else:
            print(f"http://127.0.0.1:{port}{route}")
            WSGIRunner.LogAttached(('0.0.0.0', port,), app, logger).serve_forever()


    class LogAttached(WSGIServer):
        """
        Attach logger to the WSGI server
        """
        def __init__(self, listener, application, logger:CustomisedLogs, **ssl_args):
            self.logger:CustomisedLogs = logger
            self.handler_class: WSGIRunner.LogAttached.SSLSuppressed | None = None
            super().__init__(listener, application=application, log=None, error_log=None, handler_class=WSGIRunner.LogAttached.SSLSuppressed, **ssl_args)


        def handle(self, sock, address):
            try:
                handler = self.handler_class(sock, address, self)
                handler.handle()
            except:
                pass


        def wrap_socket_and_handle(self, client_socket, address):
            try:
                super().wrap_socket_and_handle(client_socket, address)
            except:
                pass


        class SSLSuppressed(WSGIHandler):
            """
            Suppress SSL Errors for the WSGI server
            """
            def __init__(self, sock, address, server):
                super().__init__(sock, address, server)


            @staticmethod
            def format_bytes(size_in_bytes):
                """
                Convert bytes to human-readable string
                :param size_in_bytes:
                :return:
                """
                if size_in_bytes == 0:
                    return "0B"
                units = ["B", "K", "M", "G", "T", "P", "E", "Z", "Y"]
                power = 0
                while size_in_bytes >= 1024 and power < len(units) - 1:
                    size_in_bytes /= 1024
                    power += 1
                return f"{size_in_bytes:.2f}{units[power]}"


            @staticmethod
            def format_log(delta, client_address, status_code, method, length, path):
                """
                Present the log string
                :param delta:
                :param client_address:
                :param status_code:
                :param method:
                :param length:
                :param path:
                :return:
                """
                return (
                    f"{delta:<{10}} "
                    f"{client_address:<{20}} "
                    f"{status_code:<{4}} "
                    f"{method:<{6}} "
                    f"{length:<{10}} "
                    f"{path}"
                )


            def process_result(self):
                try:
                    super().process_result()
                except:
                    pass


            def log_error(self, msg, *args):
                """
                Log errors (overridden)
                :param msg:
                :param args:
                :return:
                """
                pass


            def log_request(self) -> None:
                """
                Log the current context (overridden)
                :return:
                """
                length = '%s' % self.format_bytes(self.response_length) or '-B'
                if self.time_finish:
                    delta = '%.3fms' % ((self.time_finish - self.time_start)*1000)
                else:
                    delta = '-ms'
                client_address = '[%s]' % (self.headers.get("X-Forwarded-For") if self.headers.get("X-Forwarded-For") is not None else (self.client_address[0] if isinstance(self.client_address, tuple) else self.client_address))
                logger:CustomisedLogs = self.server.logger
                color = logger.Colors.green_800 if self.code == -200 else logger.Colors.green_700_accent if self.code == 200 else logger.Colors.green_400 if 200 < self.code < 400 else logger.Colors.red_800
                #logger.log(color, self.application.name, self.format_log(delta, client_address , self.code, self.command, length, self.path))
