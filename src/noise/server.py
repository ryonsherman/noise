import logging
import os
import threading
import time
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from io import BytesIO

log = logging.getLogger("noise")

LIVERELOAD_SCRIPT = """
<script>
(function() {
  var evtSource = new EventSource('/__noise_reload');
  evtSource.addEventListener('message', function(e) {
    if (e.data === 'reload') {
      window.location.reload();
    }
  });
})();
</script>
"""


class DevServer:
    def __init__(self, build_path, source_paths, rebuild):
        self.build_path = build_path
        self.source_paths = source_paths
        self.rebuild = rebuild
        self._version = 0
        self._listeners = []
        self._lock = threading.Lock()

    def start(self, host='127.0.0.1', port=8000):
        handler = partial(DevServerHandler, self, directory=str(self.build_path))
        httpd = HTTPServer((host, port), handler, bind_and_activate=False)
        httpd.allow_reuse_address = True
        httpd.server_bind()
        httpd.server_activate()

        watcher = threading.Thread(target=self._watch, daemon=True)
        watcher.start()

        addr = httpd.server_address
        log.info("Serving at http://%s:%d", addr[0], addr[1])
        log.info("Watching for changes...")
        httpd.serve_forever()

    def _watch(self):
        mtimes = {}
        for p in self.source_paths:
            try:
                mtimes[p] = os.stat(p).st_mtime
            except OSError:
                pass
        while True:
            time.sleep(1)
            changed = False
            for p in self.source_paths:
                try:
                    mtime = os.stat(p).st_mtime
                except OSError:
                    continue
                if mtime != mtimes.get(p):
                    mtimes[p] = mtime
                    changed = True
            if changed:
                log.info("Source change detected, rebuilding...")
                self.rebuild()
                with self._lock:
                    self._version += 1
                    for q in self._listeners:
                        q.put_nowait(('reload',))
                        self._listeners.remove(q)

    def add_listener(self, q):
        with self._lock:
            self._listeners.append(q)

    def remove_listener(self, q):
        with self._lock:
            if q in self._listeners:
                self._listeners.remove(q)


class DevServerHandler(SimpleHTTPRequestHandler):
    def __init__(self, server, *args, **kwargs):
        self._dev_server = server
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/__noise_reload':
            self._sse_loop()
        else:
            super().do_GET()

    def _sse_loop(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.end_headers()
        from queue import Queue
        q = Queue()
        self._dev_server.add_listener(q)
        try:
            while True:
                msg = q.get()
                if msg[0] == 'reload':
                    self.wfile.write(b'data: reload\n\n')
                    self.wfile.flush()
                    break
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            self._dev_server.remove_listener(q)

    def send_head(self):
        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            return super().send_head()
        ctype = self.guess_type(path)
        if ctype == 'text/html':
            with open(path, 'rb') as f:
                content = f.read()
            injection = LIVERELOAD_SCRIPT.encode()
            content = content.replace(b'</body>', injection + b'</body>')
            f = BytesIO()
            f.write(content)
            f.seek(0)
            self.send_response(200)
            self.send_header('Content-Type', ctype + '; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Last-Modified', self.date_time_string(os.path.getmtime(path)))
            self.end_headers()
            return f
        return super().send_head()

    def log_message(self, fmt, *args):
        log.info(fmt, *args)
