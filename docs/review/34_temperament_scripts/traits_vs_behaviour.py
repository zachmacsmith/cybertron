import pyarrow.parquet as pq, glob, json, collections, math, statistics as st
def tbl(n): 
    out=[]
    for p in glob.glob(f'runs/*/*/{n}.parquet'):
        out.append(pq.read_table(p).to_pydict())
    return out
TR=['risk','trust','honesty','assertiveness','patience','reciprocity','talkativeness']
A={}
for d in tbl('agents'):
    for i in range(len(d['agent'])):
        tr={t:d['personality_'+t][i] for t in TR}
        if any(v is None for v in tr.values()): continue
        A[(d['run_id'][i],d['agent'][i])]={'model':(d['model'][i] or '?').replace('claude-','').split('-')[0],'tr':tr,'arch':d['archetype'][i],'cls':d['cls'][i]}
B=collections.defaultdict(collections.Counter)
for d in tbl('turns'):
    for i in range(len(d['agent'])):
        if d['inherited'][i]: continue
        k=(d['run_id'][i],d['agent'][i]); B[k]['turns']+=1
        try: acts=json.loads(d['actions_json'][i] or '[]')
        except: acts=[]
        B[k]['acts']+=len(acts)
        kinds=collections.Counter(a.get('action') for a in acts if isinstance(a,dict))
        for a,n in kinds.items(): B[k]['a:'+str(a)]+=n
        B[k]['reason_chars']+=len(d['stated_reasoning'][i] or '')
for d in tbl('messages'):
    for i in range(len(d['sender'])):
        if d['inherited'][i]: continue
        k=(d['run_id'][i],d['sender'][i]); t=d['type'][i]; L=len(d['text'][i] or '')
        if t=='dm': B[k]['dm']+=1; B[k]['dm_chars']+=L
        elif t in ('post','channel_post','anon_post','publish'): B[k]['post']+=1; B[k]['post_chars']+=L
for d in tbl('attacks'):
    for i in range(len(d.get('attacker',[]))):
        B[(d['run_id'][i],d['attacker'][i])]['attacks']+=1
def m(k,b):
    T=max(b['turns'],1)
    acts={x[2:]:n for x,n in b.items() if x.startswith('a:')}
    tot=sum(acts.values()) or 1
    ent=-sum(n/tot*math.log(n/tot) for n in acts.values()) if acts else 0
    return {'dm_per_turn':b['dm']/T,'dm_len':(b['dm_chars']/b['dm']) if b['dm'] else None,'post_len':(b['post_chars']/b['post']) if b['post'] else None,'post_per_turn':b['post']/T,
            'propose_per_turn':(acts.get('propose',0)+acts.get('amend',0))/T,'attacks_per_turn':b['attacks']/T,
            'transfer_per_turn':acts.get('transfer',0)/T,'lend_per_turn':acts.get('lend',0)/T,'accuse_per_turn':acts.get('accuse',0)/T,
            'deceive_per_turn':(acts.get('forge_dm',0)+acts.get('anon_post',0))/T,'reason_len':b['reason_chars']/T,'action_entropy':ent,'acts_per_turn':b['acts']/T}
rows=[]
for k,a in A.items():
    b=B.get(k)
    if not b or b['turns']<3: continue
    tr=a['tr']; shown=set(sorted(tr,key=lambda t:-abs(tr[t]-0.5))[:4])
    rows.append({'run':k[0],'agent':k[1],**a,'shown':shown,'beh':m(k,b)})
# z within run x model
grp=collections.defaultdict(list)
for r in rows: grp[(r['run'],r['model'])].append(r)
BEH=list(rows[0]['beh'].keys())
for g in grp.values():
    for b in BEH:
        vals=[r['beh'][b] for r in g if r['beh'][b] is not None]
        if len(vals)<3: 
            for r in g: r.setdefault('z',{})[b]=None
            continue
        mu=st.mean(vals); sd=st.pstdev(vals) or None
        for r in g: r.setdefault('z',{})[b]=None if (r['beh'][b] is None or not sd) else (r['beh'][b]-mu)/sd
def rank(x):
    s=sorted(range(len(x)),key=lambda i:x[i]); rk=[0]*len(x)
    for j,i in enumerate(s): rk[i]=j
    return rk
def spear(xs,ys):
    pr=[(x,y) for x,y in zip(xs,ys) if x is not None and y is not None]
    if len(pr)<15: return None,len(pr)
    a,b=zip(*pr); ra,rb=rank(a),rank(b)
    n=len(a); ma,mb=st.mean(ra),st.mean(rb)
    cov=sum((x-ma)*(y-mb) for x,y in zip(ra,rb)); va=sum((x-ma)**2 for x in ra); vb=sum((y-mb)**2 for y in rb)
    return cov/math.sqrt(va*vb),n
print('agents',len(rows),'runs',len({r['run'] for r in rows}), collections.Counter(r['model'] for r in rows))
H=[('talkativeness','post_len'),('assertiveness','post_len'),('talkativeness','dm_per_turn'),('talkativeness','dm_len'),('talkativeness','post_per_turn'),('talkativeness','reason_len'),
   ('assertiveness','propose_per_turn'),('assertiveness','post_per_turn'),('assertiveness','dm_per_turn'),
   ('risk','attacks_per_turn'),('risk','lend_per_turn'),('trust','transfer_per_turn'),('trust','lend_per_turn'),
   ('honesty','deceive_per_turn'),('reciprocity','accuse_per_turn'),('reciprocity','attacks_per_turn'),('patience','acts_per_turn')]
print(f"{'trait':14s} {'behaviour':18s} | shown r (n) | not-shown r (n)")
for t,b in H:
    sh=[r for r in rows if t in r['shown']]; ns=[r for r in rows if t not in r['shown']]
    r1,n1=spear([r['tr'][t] for r in sh],[r['z'][b] for r in sh]); r2,n2=spear([r['tr'][t] for r in ns],[r['z'][b] for r in ns])
    f=lambda r,n: f"{r:+.2f} ({n})" if r is not None else f"  -  ({n})"
    print(f"{t:14s} {b:18s} | {f(r1,n1):12s} | {f(r2,n2)}")
# archetypes
print('\nARCHETYPES: mean z vs no-archetype')
for b in ('dm_per_turn','dm_len','post_per_turn','action_entropy','attacks_per_turn','deceive_per_turn','propose_per_turn','transfer_per_turn'):
    out=[]
    for ar in ('gossip','secretive','chaotic','paranoid','zealot','opportunist','loyalist','contrarian','aggressor'):
        v=[r['z'][b] for r in rows if r['arch']==ar and r['z'][b] is not None]
        if len(v)>=8: out.append(f"{ar}:{st.mean(v):+.2f}({len(v)})")
    print(b, ' '.join(out))
# message length by talkativeness bucket, shown only
print('\nDM length (chars) by shown talkativeness level, per model')
for mdl in ('haiku','sonnet','opus'):
    for lv,(lo,hi) in (('low',(0,.35)),('mid',(.35,.65)),('high',(.65,1.01))):
        v=[r['beh']['dm_len'] for r in rows if r['model']==mdl and 'talkativeness' in r['shown'] and lo<=r['tr']['talkativeness']<hi and r['beh']['dm_len']]
        d=[r['beh']['dm_per_turn'] for r in rows if r['model']==mdl and 'talkativeness' in r['shown'] and lo<=r['tr']['talkativeness']<hi]
        if v: print(f"  {mdl:6s} {lv:4s} DM len {st.mean(v):6.0f}  DMs/turn {st.mean(d):.2f}  (n={len(v)})")
