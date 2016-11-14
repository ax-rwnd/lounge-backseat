#include <mysql++.h>
#include <iostream>
#include <iomanip>

using namespace std;

int main(int argc, char *argv[]) {
	char *user, *pass;

	if (argc!=3) {
		cerr << "Usage: sqltest username password" << endl;
		return 1;
	} else {
		user = argv[1];
		pass = argv[2];
	}

	// Connect to the sample database.
	mysqlpp::Connection conn(false);

	if (conn.connect("loungematic", "127.0.0.1", user, pass)) {
		// Retrieve a subset of the sample stock table set up by resetdb
		// and display it.
		mysqlpp::Query query = conn.query("select item from stock");
		if (mysqlpp::StoreQueryResult res = query.store()) {
			cout << "We have:" << endl;
			mysqlpp::StoreQueryResult::const_iterator it;
			for (it = res.begin(); it != res.end(); ++it) {
				mysqlpp::Row row = *it;
				cout << '\t' << row[0] << endl;
			}
		} else {
			cerr << "Failed to get item list: " << query.error() << endl;
			return 1;
		}
		return 0;
	} else {
		cerr << "DB connection failed: " << conn.error() << endl;
		return 1;
	}
}
