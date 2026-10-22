import pyarrow.parquet as pq, glob, json, re, collections, statistics as st
TR=['risk','trust','honesty','assertiveness','patience','reciprocity','talkativeness']
A={}
for p in glob.glob('runs/*/*/agents.parquet'):
    d=pq.read_table(p).to_pydict()
    for i in range(len(d['agent'])):
        tr={t:d['personality_'+t][i] for t in TR}
        if None in tr.values(): continue
        shown=sorted(tr,key=lambda t:-abs(tr[t]-.5))[:4]
        A[(d['run_id'][i],d['agent'][i])]=(tr,shown,(d['model'][i] or '?').replace('claude-','').split('-')[0])
DEC=re.compile(r"\b(bluff|pretend|mislead|deceiv|decept|lie to|lying|false(ly)? (claim|promise)|without telling|not tell|hide (my|that|the)|keep (it|this) (secret|quiet)|feign|fake)\w*",re.I)
SELF={'risk':re.compile(r"\b(cautious|reserves|gamble|risk[- ]?(averse|taker))",re.I),'honesty':re.compile(r"\b(I never (lie|state)|honest|deceive when)",re.I),
      'talkativeness':re.compile(r"\b(few, short|keep (it|messages) short|brief(ly)?)\b",re.I),'reciprocity':re.compile(r"\b(punish|retaliat|forgive)",re.I),
      'patience':re.compile(r"\b(long run|end of the game|wait for|payoff)",re.I),'trust':re.compile(r"\b(trust|defect)",re.I),'assertiveness':re.compile(r"\b(lead|set the agenda|propose)",re.I)}
dec=collections.defaultdict(list); self_=collections.defaultdict(lambda: collections.defaultdict(list))
for p in glob.glob('runs/*/*/turns.parquet'):
    d=pq.read_table(p,columns=['run_id','agent','inherited','stated_reasoning']).to_pydict()
    per=collections.defaultdict(lambda:[0,0]); hits=collections.defaultdict(collections.Counter)
    for i in range(len(d['agent'])):
        if d['inherited'][i]: continue
        k=(d['run_id'][i],d['agent'][i]); s=d['stated_reasoning'][i] or ''
        per[k][0]+=1; per[k][1]+= bool(DEC.search(s))
        for t,rx in SELF.items(): hits[k][t]+=bool(rx.search(s))
    for k,(n,h) in per.items():
        if k not in A or n<3: continue
        tr,shown,m=A[k]
        if 'honesty' in shown:
            lv='low' if tr['honesty']<.35 else ('high' if tr['honesty']>.65 else 'mid')
            dec[(m,lv)].append(h/n)
        for t in SELF:
            self_[t]['shown' if t in shown else 'not'].append(hits[k][t]/n)
print('Share of turns whose reasoning talks about deceiving, by shown honesty level:')
for m in ('haiku','sonnet','opus'):
    print(' ',m, {lv:(round(st.mean(dec[(m,lv)])*100,1), len(dec[(m,lv)])) for lv in ('low','mid','high') if dec[(m,lv)]})
print('Share of turns echoing the trait wording, shown vs not shown:')
for t in SELF: print(' ',t, round(st.mean(self_[t]['shown'])*100,1), 'vs', round(st.mean(self_[t]['not'])*100,1))
