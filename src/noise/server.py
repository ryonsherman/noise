import logging
import os
import threading
import time
import traceback
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
    def __init__(self, build_path, source_root, rebuild):
        self.build_path = build_path
        self.source_root = source_root
        self.rebuild = rebuild
        self._listeners = []
        self._lock = threading.Lock()

    def start(self, host='127.0.0.1', port=8000):
        handler = partial(DevServerHandler, self, directory=str(self.build_path))

        try:
            httpd = HTTPServer((host, port), handler, bind_and_activate=False)
        except OSError as e:
            log.error("Failed to bind to %s:%d — %s", host, port, e)
            return

        httpd.allow_reuse_address = True
        httpd.server_bind()
        httpd.server_activate()

        watcher = threading.Thread(target=self._watch, daemon=True)
        watcher.start()

        addr = httpd.server_address
        log.info("Serving at http://%s:%d", addr[0], addr[1])
        log.info("Watching for changes...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            log.info("Shutting down...")
            httpd.shutdown()

    def _watch(self):
        mtimes = {}
        while True:
            time.sleep(1)
            changed = False
            paths = []
            try:
                for root, dirs, files in os.walk(str(self.source_root)):
                    dirs[:] = [d for d in dirs if d not in ('build', '.git', '__pycache__', '.gradle')]
                    for f in files:
                        paths.append(os.path.join(root, f))
            except OSError as e:
                log.error("Watch error walking source tree: %s", e)
                continue
            for p in paths:
                try:
                    mtime = os.stat(p).st_mtime
                except OSError:
                    continue
                prev = mtimes.get(p)
                if prev is None or mtime != prev:
                    mtimes[p] = mtime
                    changed = True
            if changed:
                log.info("Source change detected, rebuilding...")
                try:
                    self.rebuild()
                    log.info("Build complete, reloading browsers")
                except Exception as e:
                    log.error("Rebuild failed: %s", e)
                    for line in traceback.format_exc().splitlines():
                        log.error("  %s", line)
                    continue
                with self._lock:
                    for q in self._listeners:
                        try:
                            q.put_nowait(None)
                        except Exception:
                            pass
                    self._listeners.clear()

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
                if msg is None:
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
            try:
                with open(path, 'rb') as f:
                    content = f.read()
            except OSError as e:
                log.error("Error reading %s: %s", path, e)
                self.send_error(404, "Not found")
                return None
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

    def log_error(self, fmt, *args):
        log.error(fmt, *args)
