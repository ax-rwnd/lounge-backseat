#include "pistache/endpoint.h"

using namespace Net;

class HelloHandler : public Http::Handler {
	public:
		HTTP_PROTOTYPE(HelloHandler)

		void onRequest(const Http::Request& request, Http::ResponseWriter response) {
			response.send(Http::Code::Ok, "Hello World");
		}
};

int main (int argc, char **argv) {
	Net::Address addr(Net::Ipv4::any(), Net::Port(5000));

	auto opts = Http::Endpoint::options().threads(1);
	Http::Endpoint server(addr);
	server.init(opts);
	server.setHandler(std::make_shared<HelloHandler>());
	server.serve();
}
