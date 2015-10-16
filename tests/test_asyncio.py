import asyncio
import configparser
import os
import unittest
from functools import wraps

from bonsai import LDAPClient
from bonsai import LDAPEntry
import bonsai.errors

def asyncio_test(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(func)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper


class AIOLDAPConnectionTest(unittest.TestCase):
    """ Test AIOLDAPConnection object. """
    def setUp(self):
        """ Set LDAP URL and open connection. """
        curdir = os.path.abspath(os.path.dirname(__file__))
        self.cfg = configparser.ConfigParser()
        self.cfg.read(os.path.join(curdir, 'test.ini'))
        self.url = "ldap://%s:%s/%s?%s?%s" % (self.cfg["SERVER"]["host"], \
                                        self.cfg["SERVER"]["port"], \
                                        self.cfg["SERVER"]["basedn"], \
                                        self.cfg["SERVER"]["search_attr"], \
                                        self.cfg["SERVER"]["search_scope"])
        self.basedn = self.cfg["SERVER"]["basedn"]
        self.client = LDAPClient(self.url)
        self.client.set_credentials("SIMPLE", (self.cfg["SIMPLEAUTH"]["user"],
                                          self.cfg["SIMPLEAUTH"]["password"]))
        
    @asyncio_test
    def test_connection(self):
        conn = yield from self.client.connect(True)
        self.assertIsNotNone(conn)
        self.assertFalse(conn.closed)
    
    @asyncio_test
    def test_search(self):
        with (yield from self.client.connect(True)) as conn:
            res = yield from conn.search()
            self.assertIsNotNone(res)
   
    @asyncio_test
    def test_add_and_delete(self):
        with (yield from self.client.connect(True)) as conn:
            entry = LDAPEntry("cn=async_test,%s" % self.basedn)
            entry['objectclass'] = ['top', 'inetOrgPerson', 'person',
                                    'organizationalPerson']
            entry['sn'] = "async_test"
            try:
                yield from conn.add(entry)
            except bonsai.errors.AlreadyExists:
                yield from conn.delete(entry.dn)
                yield from conn.add(entry)
            except:
                self.fail("Unexcepected error.")
            res = yield from conn.search()
            self.assertIn(entry, res)
            entry.delete()
            res = yield from conn.search()
            self.assertNotIn(entry, res)

    @asyncio_test
    def test_modify_and_rename(self):
        with (yield from self.client.connect(True)) as conn:
            entry = LDAPEntry("cn=async_test,%s" % self.basedn)
            entry['objectclass'] = ['top', 'inetOrgPerson', 'person',
                                    'organizationalPerson']
            entry['sn'] = "async_test"
            try:
                yield from conn.add(entry)
            except bonsai.errors.AlreadyExists:
                yield from conn.delete(entry.dn)
                yield from conn.add(entry)
            except:
                self.fail("Unexcepected error.")
            entry['sn'] = "async_test2"
            yield from entry.modify()
            yield from entry.rename("cn=async_test2,%s" % self.basedn)
            res = yield from conn.search(entry.dn, 0, attrlist=['sn'])
            self.assertEqual(entry['sn'], res[0]['sn'])
            res = yield from conn.search("cn=async_test,%s" % self.basedn, 0)
            self.assertEqual(res, [])
            yield from conn.delete(entry.dn)

    def test_obj_err(self):
        entry = LDAPEntry("cn=async_test,%s" % self.basedn)
        entry['objectclass'] = ['top', 'inetOrgPerson', 'person',
                                'organizationalPerson']
        @asyncio_test
        def err():
            with (yield from self.client.connect(True)) as conn:
                yield from conn.add(entry)
        self.assertRaises(bonsai.errors.ObjectClassViolation, err)

    @asyncio_test
    def test_whoami(self):
        """ Test whoami. """
        with (yield from self.client.connect(True)) as conn:
            obj = yield from conn.whoami()
            expected_res = "dn:%s" % self.cfg["SIMPLEAUTH"]["user"]
            self.assertEqual(obj, expected_res)
            
if __name__ == '__main__':
    unittest.main()
