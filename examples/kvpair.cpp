#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <map>

typedef std::map<std::string, std::string> Config;

//Inspired by http://stackoverflow.com/questions/25829143/c-trim-whitespace-from-a-string
std::string trim(std::string& str) {
	size_t beg = str.find_first_not_of(" \t");
	size_t end = str.find_last_not_of(" \t");
	return str.substr(beg, (end-beg+1));
}

//Opens path, reads kv-pairs from every line and returns a config
//  mapping.
Config configFromFile(const char *path) {
	Config kvpairs;
	std::fstream fs;
	std::string buffer;

	fs.open(path, std::fstream::in);

	while (std::getline(fs, buffer)) {
		std::istringstream iss(buffer);
		std::string key, value;

		if (std::getline(iss, key, '=')) {
			if (trim(key)[0] == '#')  {
				continue;
			} else if (std::getline(iss, value)) {
				kvpairs[key] = value;
			}
		}
	}

	fs.close();
	return kvpairs;
}

int main (int argc, char **argv) {
	Config test = configFromFile("testkv.pair");
	std::cout<<test["user"] << std::endl;
	std::cout<<test["pass"] << std::endl;
}
