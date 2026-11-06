import random,itertools,copy,math
R=random.Random(7342)
TASKS=[]
def task(id,spec,name,ref,cases):
 for args,expected in cases:
  got=ref(*copy.deepcopy(args)); assert got==expected or (isinstance(got,float) and math.isclose(got,expected,abs_tol=1e-8)),(id,args,got,expected)
 TASKS.append(dict(id=id,spec=spec,name=name,ref=ref,cases=cases))
def merge(xs):
 out=[]
 for a,b in sorted(xs):
  if out and a<=out[-1][1]:out[-1]=(out[-1][0],max(b,out[-1][1]))
  else:out.append((a,b))
 return out
xs=[[],[(1,1)],[(3,4),(1,2),(2,3)],[(1,10),(2,3)],[(1,2),(3,4)]]
xs += [[tuple(sorted((R.randint(-8,8),R.randint(-8,8)))) for _ in range(R.randint(0,9))] for _ in range(15)]
task('merge','merge_intervals(intervals): list of integer closed (start,end) tuples, start<=end. Return sorted list of tuples merging iff next start <= current end. Do not merge merely adjacent integers (1,2) and (3,4). Empty -> [].','merge_intervals',merge,[((x,),merge(x)) for x in xs])
def energy(s):return sum((s[i][0]-s[i-1][0])*(s[i][1]+s[i-1][1])/2/3600 for i in range(1,len(s)))
ss=[[],[(0,3)],[(0,10),(0,200),(3600,200)],[(0,-100),(3600,100)],[(0,0),(3600,100)]]
for _ in range(15):
 ts=0;s=[]
 for j in range(R.randint(0,10)):ts+=R.choice([0,0,60,1800]);s.append((ts,R.randint(-500,500)))
 ss.append(s)
task('energy','integrate_wh(samples): timestamp seconds, signed power watts; timestamps nondecreasing. Sum trapezoids between every adjacent pair divided by 3600. Duplicate timestamps have zero interval area but the later sample is used for the next interval. Fewer than 2 -> 0.','integrate_wh',energy,[((s,),energy(s)) for s in ss])
def topo(ns,es):
 for p in itertools.permutations(sorted(ns)):
  pos={n:i for i,n in enumerate(p)}
  if all(pos[a]<pos[b] for a,b in es):return list(p)
 return None
cases=[(([],[]),[]),((['a'],[('a','a')]),None),((['b','a'],[('a','b'),('a','b')]),['a','b'])]
for _ in range(17):
 ns=list('abcde')[:R.randint(1,5)];es=[(R.choice(ns),R.choice(ns)) for _ in range(R.randint(0,8))];cases.append(((ns,es),topo(ns,es)))
task('topo','topo_order(nodes, edges): nodes are unique strings; edges (source,target), all endpoints in nodes. Return lexicographically smallest topological order, None for ANY cycle including a self-edge. Duplicate edges count once. Empty -> [].','topo_order',topo,cases)
def nearest(qs,ss,tol):
 out=[]
 for q in qs:
  avail=[(abs(t-q),t,i) for i,t in enumerate(ss) if abs(t-q)<=tol]
  out.append(min(avail)[2] if avail else None)
 return out
cases=[(([2,4],[1,3,3,5],1),[0,1]),(([0],[],3),[None]),(([],[2],0),[])]
for _ in range(17):
 qs=[R.randint(-10,10) for _ in range(6)];ss=sorted(R.randint(-10,10) for _ in range(R.randint(0,8)));tol=R.randint(0,4);cases.append(((qs,ss,tol),nearest(qs,ss,tol)))
task('nearest','nearest_indices(queries, samples, tolerance): queries integer timestamps, samples sorted nondecreasing integer timestamps, tolerance>=0. For each query return index of closest sample within tolerance inclusive, else None. Tie: earlier timestamp, then lowest index for duplicate timestamps. Samples may be reused.','nearest_indices',nearest,cases)
def rolling(xs,w):
 return [sum(v for v in xs[max(0,i-w+1):i+1] if v is not None)/sum(v is not None for v in xs[max(0,i-w+1):i+1]) if any(v is not None for v in xs[max(0,i-w+1):i+1]) else None for i in range(len(xs))]
cases=[(([None,None,0,4],2),[None,None,0,2]),(([],1),[])]
for _ in range(18):
 xs=[R.choice([None,0,-2,3,7]) for i in range(R.randint(1,10))];w=R.randint(1,5);cases.append(((xs,w),rolling(xs,w)))
task('rolling','rolling_mean(values, window): window positive integer. For each index average non-None entries among last window POSITIONS including current; prefix uses fewer positions. Return None if no numeric entry. Zero is a valid numeric value.','rolling_mean',rolling,cases)
def lru(cap,cmds):
 d={};order=[];outs=[]
 for c in cmds:
  op,k=c[:2]
  if op=='get':
   outs.append(d.get(k));
   if k in d:order.remove(k);order.append(k)
  elif cap:
   if k in d:order.remove(k)
   d[k]=c[2];order.append(k)
   if len(order)>cap:del d[order.pop(0)]
 return outs
cases=[((0,[('put','a',1),('get','a')]),[None]),((2,[('put','a',1),('put','b',2),('get','a'),('put','c',3),('get','b'),('get','a')]),[1,None,1])]
for _ in range(18):
 cap=R.randint(0,3);cmds=[]
 for i in range(15):
  k=R.choice('abc');cmds.append(('get',k) if R.random()<.5 else ('put',k,R.randint(0,9)))
 cases.append(((cap,cmds),lru(cap,cmds)))
task('lru','simulate_lru(capacity, commands): capacity nonnegative number of entries. Commands ("put",key,value), ("get",key), key str/value int. Return list of results of get only, None on miss. Get hit and put/update make key most recently used; eviction removes least recent. Capacity 0 stores nothing.','simulate_lru',lru,cases)
def patch(target,p):
 if not isinstance(p,dict):return copy.deepcopy(p)
 out=copy.deepcopy(target) if isinstance(target,dict) else {}
 for k,v in p.items():
  if v is None:out.pop(k,None)
  else:out[k]=patch(out.get(k),v)
 return out
cases=[(({'a':1,'b':{'c':2,'d':3}},{'a':None,'b':{'c':4}}),{'b':{'c':4,'d':3}}),(([1,2],{'x':1}),{'x':1}),(({'a':1},None),None),(({'a':[1,2]},{'a':[3]}),{'a':[3]}),(({'a':1},{'z':None}),{'a':1}),(({},{}),{}),(({'a':{'b':1}},{'a':None}),{}),(({'a':1},{'a':{'z':2}}),{'a':{'z':2}})]
task('patch','merge_patch(target, patch): JSON merge patch. If patch is not a dict, return an independent deep copy of patch. If patch dict, start with deep copy of target if dict else {}. For each key, None deletes it; any other value recursively patches that value. Lists replace, not concatenate. Never mutate or alias mutable inputs.','merge_patch',patch,cases)
def deltas(vals):
 if len(vals)<2:return 0
 return sum(b-a if b>=a else b for a,b in zip(vals,vals[1:]))
vs=[[],[5],[0,3,8],[10,2,7],[5,5,0,4],[100,0,0,10]]+[[R.randint(0,20) for _ in range(10)] for _ in range(14)]
task('repo_counter','Mini repository file energy.py has buggy function:\ndef counter_delta(readings):\n    return readings[-1] - readings[0]\nFix it. readings are nonnegative cumulative Wh measurements. Sum adjacent increases; when counter decreases it reset to zero and that interval contributes the new reading. Fewer than 2 -> 0. Return corrected counter_delta function only.','counter_delta',deltas,[((v,),deltas(v)) for v in vs])
def fresh(c,now,ttl):return {k:v[1] for k,v in c.items() if 0<=now-v[0]<ttl}
cases=[(({'a':(90,1),'b':(100,2),'c':(101,3),'d':(89,4)},100,10),{'b':2}),(({},0,0),{}),(({'a':(0,0)},0,0),{}),(({'a':(3,None)},4,2),{'a':None})]
for _ in range(16):
 c={k:(R.randint(0,20),R.choice([None,0,1,2])) for k in 'abcd'};now=R.randint(0,20);ttl=R.randint(0,8);cases.append(((c,now,ttl),fresh(c,now,ttl)))
task('repo_ttl','Mini repository cache.py has bug:\ndef fresh_entries(cache, now, ttl):\n    return {k: value for k, (timestamp, value) in cache.items() if now-timestamp <= ttl}\nFix fresh_entries: return values whose ages satisfy 0 <= now-timestamp < ttl. Future entries are excluded, exact expiry is excluded, ttl=0 returns {}. Do not mutate cache.','fresh_entries',fresh,cases)
if __name__=='__main__': print('REFERENCE_SELF_TEST_OK',[(t['id'],len(t['cases'])) for t in TASKS])
