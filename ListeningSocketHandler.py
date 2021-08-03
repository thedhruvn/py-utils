"""
    ListeningSocketHandler
    ======================
    A python logging handler.
    logging.handlers.SocketHandler is a TCP Socket client that sends log
    records to a tcp server.
    This class is the opposite.
    When a TCP client connects (e.g. telnet or netcat), new log records
    are sent through the tcp connection.
"""
import logging
import socket
import sys
import threading
import unittest

class ListeningSocketHandler(logging.Handler):
    def __init__(self, port=0, ipv6=False):
        super(ListeningSocketHandler, self).__init__()
        if ipv6:
            a = socket.socket(socket.AF_INET6)
            a.bind(("::", port))
        else:
            a = socket.socket(socket.AF_INET)
            a.bind(("0.0.0.0", port))
        self._acceptor = a
        self._acceptor.listen(1)
        self._conn = None

        def start_listening(tsh):
            while True:
                try:
                    conn, addr = tsh._acceptor.accept()
                    tsh._conn = conn.makefile('w')
                except socket.error:
                    pass

        self._accept_thread = threading.Thread(target=start_listening, args=(self,))
        self._accept_thread.daemon = True
        self._accept_thread.start()

    def emit(self, record):
        if self._conn is None:
            # Silently drop the log
            return
        try:
            self._conn.write(record.getMessage())
            self._conn.write("\n")
            self._conn.flush()
        except socket.error:
            self._conn = None

    def flush(self):
        if self._conn:
            self._conn.flush()

    def getsockname(self):
        return self._acceptor.getsockname()