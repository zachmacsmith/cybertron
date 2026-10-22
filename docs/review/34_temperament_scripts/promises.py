import pyarrow.parquet as pq, glob, json, re, collections, statistics as st
TR=['risk','trust','honesty','assertiveness','patience','reciprocity','talkativeness']
A={}
for p in glob.glob('runs/*/*/agents.parquet'):
    d=pq.read_table(p).to_pydict()
    for i in range(len(d['agent'])):
        tr={t:d['personality_'+t][i] for t in TR}
        if None in tr.values(): continue
        A[(d['run_id'][i],d['agent'][i])]=(tr,sorted(tr,key=lambda t:-abs(tr[t]-.5))[:4],(d['model'][i] or '?').replace('claude-','').split('-')[0],d['goal_primary'][i])
def lvl(x): return 'low' if x<.35 else ('high' if x>.65 else 'mid')
PAY=re.compile(r"\bI(?:'ll| will| am going to| shall)\s+(?:also\s+|now\s+|then\s+)?(?:send|pay|transfer|give|repay|return|deliver)\b",re.I)
VOTE=re.compile(r"\b(?:I(?:'ll| will)\s+(?:also\s+)?vote|my vote is|voting)\s+(aye|yes|no|nay|for|against)\b[^.]{0,40}?\bB(\d+)",re.I)
res=collections.defaultdict(list)   # key -> list of (kept, sender)
for rp in glob.glob('runs/*/*/'):
    try:
        M=pq.read_table(rp+'messages.parquet',columns=['run_id','round','inherited','type','sender','recipients_json','text']).to_pydict()
        E=pq.read_table(rp+'events.parquet',columns=['run_id','round','type','agent','inherited','data_to','data_json']).to_pydict()
    except Exception: continue
    tr_ev=collections.defaultdict(list); votes=collections.defaultdict(list)
    for i in range(len(E['type'])):
        if E['inherited'][i]: continue
        t=E['type'][i]
        if t=='transfer': tr_ev[(E['agent'][i],E['data_to'][i])].append(E['round'][i])
        elif t=='vote':
            try: dj=json.loads(E['data_json'][i] or '{}')
            except: dj={}
            votes[(E['agent'][i],str(dj.get('ballot')))].append((E['round'][i],str(dj.get('choice')).lower()))
    for i in range(len(M['type'])):
        if M['inherited'][i] or M['type'][i]!='dm': continue
        s=M['sender'][i]; r=M['round'][i]; txt=M['text'][i] or ''
        try: rc=json.loads(M['recipients_json'][i] or '[]')
        except: rc=[]
        rc=[x for x in rc if x!=M['sender'][i]]
        if len(rc)!=1: continue
        to=rc[0]; key=(M['run_id'][i],s)
        if key not in A: continue
        sent=[x.strip() for x in re.split(r'(?<=[.!?])\s+',txt)]
        for sen in sent:
            cond=bool(re.search(r"\b(if|once|when|unless|after)\b",sen,re.I))
            if PAY.search(sen):
                kept=any(r<=rr<=r+2 for rr in tr_ev.get((s,to),[]))
                res['pay'].append((kept,key,cond))
            m=VOTE.search(sen)
            if m:
                ch=m.group(1).lower(); want='yes' if ch in ('aye','yes','for') else 'no'
                vv=votes.get((s,'B'+m.group(2)),[])
                if vv:   # only promises on ballots the sender actually got to vote on
                    res['vote'].append((any(c==want for _,c in vv),key,cond))
for kind in ('pay','vote'):
    L=res[kind]; print(f"\n{kind.upper()} promises: {len(L)}  kept {sum(k for k,_,_ in L)/max(len(L),1):.0%}  (unconditional {sum(k for k,_,c in L if not c)/max(1,sum(1 for _,_,c in L if not c)):.0%}, n={sum(1 for _,_,c in L if not c)})")
    by=collections.defaultdict(list)
    for k,key,c in L:
        if c: continue
        tr,shown,m,g=A[key]
        by[(m,'all')].append(k)
        tag=('shown-'+lvl(tr['honesty'])) if 'honesty' in shown else 'not-shown'
        by[('ALL',tag)].append(k); by[(m,tag)].append(k)
    for m in ('ALL','haiku','sonnet','opus'):
        print('  ',m,{t:(f"{st.mean(v):.0%}",len(v)) for (mm,t),v in sorted(by.items()) if mm==m})
