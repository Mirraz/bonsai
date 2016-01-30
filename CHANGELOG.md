# Change Log

## [0.8.1] - 2015-10-27
### Changed
- Renamed LDAPConnection's cancel method to abandon.

### Added
- Timeout support for opening an LDAP connection.

### Fixed
- Possible deadlock (by constatly locking from the main thread) during 
initialising an LDAP session on Linux.

## [0.8.0] - 2015-10-17
### Changed
- New module name (from PyLDAP) to avoid confusion with other Python LDAP
packages.
- LDAPEntry's clear and get method are rewritten in Python.
- Connection settings are accessible via properties of LDAPClient.
- Moved asyncio related code into a separate class that inherits from
LDAPConnection.
- Default async class can be change to other class implementation that
can work with non-asyncio based approaches (e.g. like Gevent).
- Names of the objects implemented in C are all lower-cased.

### Added
- Full unicode (UTF-8) support on MS Windows with WinLDAP.
- LDAPConnection.fileno() method to get the socket descriptor of the
connection.
- New methods for LDAPClient to set CA cert, client cert and client key.
- EXTERNAL SASL mechanism for binding.
- Use of authorization ID during SASL binding.
- New classes for supporting Gevent and Tornado asynchronous modules.
- Timeout parameter for LDAP operations.

### Fixed
- Own error codes start from -100 to avoid overlap with OpenLDAP's and
WinLDAP's error codes.
- New folder structure prevents the interpreter to try to load the local
files without the built C extension(, if the interpreter is started from
the module's root directory).

## [0.7.5] - 2015-07-12
### Changed
- LDAPClient.connect is a coroutine if async param is True. (Issue #1)
- The binding function on Windows uses ldap_sasl_bind instead of the
deprecated ldap_bind.
- The connection procedure (init, set TLS, bind) creates POSIX and Windows
threads to avoid I/O blocking.
- Optional error messages are appended to the Python LDAP errors.

### Added
- New open method for LDAPConnection object to build up the connection.
- New LDAPConnectIter object for initialisation, setting TLS, and binding to
the server.

### Fixed
- LDAPConnection.whoami() returns 'anonymous' after an anonymous bind.
- After failed connection LDAPClient.connect() returns ConnectionError
on MS Windows.