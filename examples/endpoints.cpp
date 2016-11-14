#include "pistache/http.h"
#include "pistache/router.h"
#include "pistache/endpoint.h"

using namespace std;
using namespace Net;

class SampleEndpoint {
private:
	typedef std::mutex Lock;
	typedef std::lock_guard<Lock> Guard;
	Lock metricsLock;

	std::shared_ptr<Net::Http::Endpoint> httpEndpoint;
	Rest::Router router;

public:
	SampleEndpoint(Net::Address addr) :
		httpEndpoint(make_shared<Net::Http::Endpoint>(addr)) {}
	
	void init(size_t thr = 2) {
		auto opts = Net::Http::Endpoint::options()
			.threads(thr)
			.flags(Net::Tcp::Options::InstallSignalHandler);
		httpEndpoint->init(opts);
		setupRoutes();
	}

	void start() {
		httpEndpoint->setHandler(router.handler());
		httpEndpoint->serve();
	}

	void shutdown() {
		httpEndpoint->shutdown();
	}

private:
	void setupRoutes() {
		using namespace Net::Rest;
		Routes::Get(router, "/api/test", Routes::bind(&SampleEndpoint::function, this));
		Routes::Get(router, "/api/nexttest", Routes::bind(&SampleEndpoint::second, this));
	}

	void function(const Rest::Request& request, Net::Http::ResponseWriter response) {
		response.cookies().add(Http::Cookie("lang", "en-US"));
		response.send(Http::Code::Ok);
	}

	void second(const Rest::Request& request, Net::Http::ResponseWriter response) {
		response.send(Http::Code::Ok, "<html><header><title>Hello World</title></header></html>");
	}
};

int main(void) {
	Net::Port port(5000);
	Net::Address addr(Net::Ipv4::any(), port);

	cout << "Cores = " << hardware_concurrency() << endl;

	SampleEndpoint endpoint (addr);
	endpoint.init(2);
	endpoint.start();
	endpoint.shutdown();

	return 0;
}
