import csv,json
from pathlib import Path
from datetime import date
A=Path('outputs/review_analysis.json'); O=Path('outputs')
if not A.exists(): raise SystemExit('Run python analyze_reviews.py first')
r=json.loads(A.read_text(encoding='utf-8'))
with open('data/official_sources.csv',encoding='utf-8-sig',newline='') as f: sources=list(csv.DictReader(f))
themes=r.get('top_3_themes',[]); quotes=r.get('three_real_review_quotes',[]); fee_issue=r.get('identified_fee_issue')
lines=['# Weekly Product Pulse','',f'**Week ending / generated:** {date.today().isoformat()}','','## Top themes']
for t in themes: lines.append(f"- **{t['theme']}** — {t['review_count']} reviews matched this theme.")
lines+=['','## Supporting user quotes']
for q in quotes:
 words=str(q['quote']).split(); excerpt=' '.join(words[:25])+('…' if len(words)>25 else '')
 lines.append(f'> “{excerpt}” — {q["date"]}, {q.get("theme","theme")}')
obs=(f"Across {r['review_count']} recent public reviews, the strongest actionable themes are "+', '.join(x['theme'] for x in themes)+'. '+(f"A recurring monetization confusion also appears: **{fee_issue}**, supported by {r.get('fee_issue_match_count',0)} reviews." if fee_issue else 'No recurring fee/charge issue met the evidence threshold.'))
lines+=['','## Key observation',obs,'','## 3 product actions',
'1. Improve image-generation/editing recovery when a result is wrong or repeated, so retries do not feel wasted.',
'2. Make usage-limit messages show what feature hit a limit, when it resets, and what upgrading changes.',
'3. Track answer-quality complaints separately from reliability failures so the right product owner can investigate each pattern.']
pulse='\n'.join(lines)
if len(pulse.split())>250: raise SystemExit(f'Pulse is {len(pulse.split())} words; must be <=250.')
O.mkdir(exist_ok=True); (O/'weekly_product_pulse.md').write_text(pulse,encoding='utf-8')

# Sources 1 and 2 are intentionally aligned to the detected usage-limit / upgrade issue.
official=[s for s in sources if s.get('url')][:2]
fee=['# Customer Fee Explainer','',f'**Identified issue:** {fee_issue or "No recurring fee issue detected"}',f'**Last checked:** {date.today().isoformat()}','']
if fee_issue:
 bullets=[
 'ChatGPT has a Free tier as well as paid plans; available features and limits vary by plan.',
 'Free-tier tools such as image generation, file/image uploads, voice, and data analysis can have separate usage limits.',
 'When an applicable Free-tier limit is reached, ChatGPT can show that the user must wait for the limit to reset.',
 'Paid plans such as ChatGPT Plus provide higher limits, but paid plans can still have usage limits.',
 'Current limits can change over time, so users should rely on the limit/reset information shown in the product and current official Help Center guidance.',
 'An upgrade prompt is an option to move to a paid plan; this explainer does not claim that upgrading is required for every ChatGPT use.'
 ]
 fee += [f'- {x}' for x in bullets]
 fee += ['','## Official sources']
 for s in official: fee.append(f"- [{s.get('title','Official source')}]({s.get('url')})")
else:
 fee += ['The review evidence does not support a recurring fee/charge issue yet. Collect more reviews before publishing a fee explanation.']
(O/'fee_explainer.md').write_text('\n'.join(fee),encoding='utf-8')
(O/'source_list.md').write_text('# Source list\n\n'+'\n'.join(f"- {s.get('title','Source')}: {s.get('url')}" for s in sources if s.get('url')),encoding='utf-8')
print('Created weekly_product_pulse.md, fee_explainer.md, source_list.md'); print('Pulse word count:',len(pulse.split()))
