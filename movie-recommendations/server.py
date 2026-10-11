"""Fixed standard-library HTTP transport. Run python3 server.py for demo data."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs
from app import dispatch, demo_service

def reject_json_constant(value):
    raise ValueError('non-finite JSON number: ' + value)

def create_server(service,host='127.0.0.1',port=8080):
    class Handler(BaseHTTPRequestHandler):
        def handle_request(self):
            parsed=urlsplit(self.path)
            try:
                raw=self.rfile.read(int(self.headers.get('Content-Length','0')))
                body=json.loads(raw,parse_constant=reject_json_constant) if raw else {}
            except (ValueError,UnicodeDecodeError):
                self.reply(400,{'error':'invalid_json'});return
            status,payload=dispatch(service,self.command,parsed.path,self.headers.get('X-User-ID'),body,
                                    {k:v[-1] for k,v in parse_qs(parsed.query,keep_blank_values=True).items()},self.headers.get('Idempotency-Key'))
            self.reply(status,payload)
        def reply(self,status,payload):
            data=b'' if status==204 else json.dumps(payload).encode()
            self.send_response(status);self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',str(len(data)));self.end_headers()
            if self.command != 'HEAD':self.wfile.write(data)
        def __getattr__(self,name):
            if name.startswith('do_'):return self.handle_request
            raise AttributeError(name)
        def log_message(self,*args):pass
    return ThreadingHTTPServer((host,port),Handler)

if __name__=='__main__':
    service=demo_service()
    try:
        with create_server(service) as server:
            print('Listening on http://127.0.0.1:8080',flush=True)
            try:server.serve_forever()
            except KeyboardInterrupt:pass
    finally:
        if hasattr(service,'close'):service.close()
