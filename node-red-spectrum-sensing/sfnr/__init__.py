from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import argparse
from importlib import import_module

class HTTPRequestHandler(BaseHTTPRequestHandler):
	def do_POST(self):
		length = int(self.headers.get('content-length'))

		s = self.rfile.read(length)
		msg = json.loads(s.decode('utf8'))

		resp = self.server.f(msg)

		self.send_response(200)
		self.end_headers()
		self.log_request()

		s = json.dumps(resp)
		self.wfile.write(s.encode('utf8'))

class SFNRBaseNode(object):
	TEMPLATE = "httprequest"

	def run_server(self):
		server_address = ('localhost', self.PORT)
		httpd = HTTPServer(server_address, HTTPRequestHandler)
		httpd.f = self.work
		httpd.serve_forever()

	@classmethod
	def install(cls):
		#node_dir = os.path.join(os.environ['HOME'], ".node-red/nodes")
		node_dir = os.path.join(os.environ['HOME'], "node_modules/node-red/nodes/sfnr")

		try:
			os.mkdir(node_dir)
		except OSError:
			pass

		for ext in ['js', 'html']:
			in_path = "templates/%s.%s.in" % (cls.TEMPLATE, ext)
			out_path = os.path.join(node_dir, "%s.%s" % (cls.SLUG, ext))

			cls._install_template(in_path, out_path)

	@classmethod
	def _install_template(cls, in_path, out_path):
		t = open(in_path).read()

		t = t % { 'port': cls.PORT,
			  'name': cls.NAME,
			  'slug': cls.SLUG,
			  'desc': cls.DESC }

		print("writing %s" % (out_path,))

		open(out_path, 'w').write(t)

def main():
	parser = argparse.ArgumentParser(description="Node-RED block starter")
	parser.add_argument("node", metavar="NODE", nargs=1)

	args = parser.parse_args()

	m = import_module("sfnr.nodes." + args.node[0])
	node = m.SFNRNode()

	print("Running node '%s' on port %d" % (args.node[0], node.PORT))
	node.run_server()

if __name__ == "__main__":
	main()