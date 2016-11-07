# Lounge-backseat
The lounge-o-matic backend server.

## API
The backend should provide an API for communicating with the database and file-
services. This will (probably) be done using *REST*-ful technologies and some
reversy proxy.

## Database access
User logins, file ownerships, playlists and so on will be stored in a database.
To maintain the mappings between the users and their data, the database should
always be accessed using the API (never directly).

## Files
Actually managing the files on the server is a task also given to the backend,
this allows the database to perform tasks that affect both the files and the
database. For instance, if one were to delete a file from one's personal
storage, the file should also be deleted from the database once it's no longer
in use.
