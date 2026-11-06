import unittest
from bench.client import validate_endpoint, build_body
class ClientTests(unittest.TestCase):
 def test_remote_denied(self):
  with self.assertRaises(ValueError):validate_endpoint('https://example.com/v1')
 def test_loopback(self):self.assertEqual(validate_endpoint('http://127.0.0.1:18081/v1/'),'http://127.0.0.1:18081/v1')
 def test_profile_cannot_replace_prompt(self):
  with self.assertRaises(ValueError):build_body('x',{'messages':[]},{'messages':[]})
 def test_native_profile(self):
  b=build_body('x',{'messages':[{'role':'user','content':'hi'}]},{'max_tokens':2048})
  self.assertNotIn('chat_template_kwargs',b)
if __name__=='__main__':unittest.main()

class TransportTests(unittest.TestCase):
 def test_no_proxy_or_redirect(self):
  import urllib.request
  from bench.client import OPENER,NoRedirect
  self.assertFalse(any(isinstance(h,urllib.request.ProxyHandler) and h.proxies for h in OPENER.handlers))
  handler=next(h for h in OPENER.handlers if isinstance(h,NoRedirect))
  self.assertIsNone(handler.redirect_request(None,None,None,None,None,None))
 def test_unknown_slot_schema_fails_closed(self):
  from unittest.mock import patch
  from bench.client import _check_slots
  for fixture in [[{}],[{'state':'processing'}],[{'is_processing':None}]]:
   with patch('bench.client.get_json',return_value=fixture):
    with self.assertRaises(RuntimeError):_check_slots('http://127.0.0.1:1')

class HealthFallbackTests(unittest.TestCase):
 def test_unknown_health_counter_fails_closed(self):
  import urllib.error
  from unittest.mock import patch
  from bench.client import _check_slots
  for value in [None,'',[],{},False,-1]:
   with patch('bench.client.get_json',side_effect=[urllib.error.HTTPError('x',404,'not found',None,None),{'slots_processing':value}]):
    with self.assertRaises(RuntimeError):_check_slots('http://127.0.0.1:1')
