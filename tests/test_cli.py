import http.server,json,pathlib,subprocess,sys,tempfile,threading,unittest
class Handler(http.server.BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  if self.path=='/slots':body=[{'is_processing':False}];status=200
  else:body={};status=404
  data=json.dumps(body).encode();self.send_response(status);self.end_headers();self.wfile.write(data)
 def do_POST(self):
  body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
  assert self.path=='/v1/chat/completions'
  assert body['model']=='fixture-model'
  data=json.dumps({'choices':[{'finish_reason':'stop','message':{'role':'assistant','content':'{"energy_wh":300,"average_w":450,"autonomy_hours":4}'}}]}).encode()
  self.send_response(200);self.end_headers();self.wfile.write(data)
class CLITests(unittest.TestCase):
 def test_end_to_end_local_fixture(self):
  server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
  thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:
   with tempfile.TemporaryDirectory() as d:
    out=pathlib.Path(d)/'result.jsonl'
    cmd=[sys.executable,'-m','bench','run','--endpoint',f'http://127.0.0.1:{server.server_port}/v1','--model','fixture-model','--suite','custom','--task','agent_units','--profile','profiles/native-default.json','--output',str(out)]
    result=subprocess.run(cmd,capture_output=True,text=True,timeout=15)
    self.assertEqual(result.returncode,0,result.stderr)
    rows=[json.loads(x) for x in out.read_text().splitlines()]
    self.assertEqual(rows[0]['task_ids'],['agent_units'])
    self.assertTrue(rows[1]['score']['functional_pass'])
    self.assertEqual(rows[1]['request']['model'],'fixture-model')
    again=subprocess.run(cmd,capture_output=True,text=True,timeout=15)
    self.assertNotEqual(again.returncode,0)
  finally:server.shutdown();server.server_close();thread.join()
if __name__=='__main__':unittest.main()
