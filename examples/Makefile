STD=c++11

NET_LIBS=-lnet
SQL_LIBS=-lmysqlpp
SQL_INCLUDES=-I/usr/include/mysql++ -I/usr/include/mysql

all:
	g++ helloworld.cpp -ohelloworld.out -std=$(STD) $(NET_LIBS) 
	g++ endpoints.cpp -oendpoints.out -std=$(STD) $(NET_LIBS) 
	g++ sql_conn.cpp -osqltest.out -std=$(STD) $(NET_LIBS) $(SQL_INCLUDES) $(SQL_LIBS)
#	g++ sqlapi.cpp -odatabase.out -std=$(STD) $(NET_LIBS) $(SQL_INCLUDES) $(SQL_LIBS)

clean:
	rm *.out
