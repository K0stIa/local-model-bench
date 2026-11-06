import unittest
from bench.sandbox import execute
from bench.core import extract_code, select_tasks
class CoreTests(unittest.TestCase):
 def test_extract(self):
  self.assertEqual(extract_code('```python\nx=1\n```'), ('x=1',False))
  self.assertEqual(extract_code('x=1'), ('x=1',True))
 def test_subset(self):
  ts=[{'id':str(i)} for i in range(20)]
  self.assertEqual(select_tasks(ts,5,42),select_tasks(ts,5,42))
  self.assertEqual(len(select_tasks(ts,5,42)),5)
 def test_ok(self): self.assertTrue(execute('assert 1+1==2')['passed'])
 def test_wrong(self): self.assertFalse(execute('assert False')['passed'])
 def test_home_hidden(self): self.assertTrue(execute('import os; assert not os.path.exists("/home")')['passed'])
 def test_network(self): self.assertTrue(execute('import socket\ns=socket.socket()\ntry: s.connect(("127.0.0.1",8080)); raise AssertionError("network open")\nexcept OSError: pass')['passed'])
 def test_timeout(self): self.assertFalse(execute('while True: pass',timeout=1)['passed'])
if __name__=='__main__': unittest.main()

class StorageTests(unittest.TestCase):
 def test_root_readonly_and_tmp_bounded(self):
  code='import os\nassert os.statvfs("/tmp").f_blocks*os.statvfs("/tmp").f_frsize <= 16*1024**2\ntry: open("/work/escape", "w"); raise AssertionError("writable root")\nexcept OSError: pass\nassert not os.path.exists("/dev/shm")'
  self.assertTrue(execute(code)['passed'])
