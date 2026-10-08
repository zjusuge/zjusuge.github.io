"""Check editable data and built page references before publishing."""
import json, re, sys
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
import yaml

ROOT=Path(__file__).resolve().parents[1]
def require(condition,message):
    if not condition: raise ValueError(message)
data={p.stem:yaml.safe_load(p.read_text(encoding='utf-8-sig')) for p in (ROOT/'_data').glob('*.yml')}
ids=set();urls=set()
for paper in data['publications']:
    for key in ['id','year','title','authors','venue','type','topic','links']:
        require(key in paper,f'Missing publication field: {key}')
    require(re.fullmatch(r'[a-z0-9-]+',paper['id']),f'Invalid anchor: {paper["id"]}')
    require(paper['id'] not in ids,f'Duplicate id: {paper["id"]}')
    ids.add(paper['id'])
    require(isinstance(paper['year'],int),'Year must be a number')
    require(paper['type'] in ['Journal article','Conference paper'],'Invalid publication type')
    require(paper['topic'] in ['Debris flows','Hydrology','Geotechnics','Algorithms'],'Invalid subject')
    for link in paper['links']:
        require(link['url'].startswith('https://'),'Publication links must use HTTPS')
        if 'doi.org/' in link['url']:
            require(link['url'].lower() not in urls,f'Duplicate DOI: {link["url"]}')
            urls.add(link['url'].lower())
for work in data['home']['selected']:
    require(work['paper_id'] in ids,f'Unknown selected paper: {work["paper_id"]}')
cv_ids=data['cv']['selected_publications']
require(len(cv_ids)==len(set(cv_ids)),'Duplicate CV selection')
require(set(cv_ids)<=ids,'Unknown selected CV publication')
require(set(data['cv']['selected_reviewing'])<=set(data['service']['reviewing']),'Selected CV reviewing must match service records')
require(bool(data['honors']),'Honor record must not be empty')
patent_numbers=set()
for patent in data['patents']:
    for key in ['number','year','status','title','authors','country','url']:
        require(bool(patent.get(key)),f'Missing patent field: {key}')
    require(patent['number'] not in patent_numbers,'Duplicate patent publication number')
    patent_numbers.add(patent['number'])
    require(patent['status'] in ['Granted','Published application'],'Invalid patent status')
    require(patent['url'].startswith('https://'),'Patent link must use HTTPS')
for profile in data['profiles']:
    require(bool(profile.get('label')) and profile.get('url','').startswith('https://'),'Invalid profile link')
for award in data['honors']:
    for key in ['title','year','context','category']:require(bool(award.get(key)),f'Missing honor field: {key}')
    require(award['category'] in ['honor','competition'],'Invalid honor category')
for paper in data['publications']:
    if paper['id'] in cv_ids:
        require(bool(paper.get('cv_role')),'Missing selected CV author role')
        require('First' in paper['cv_role'] or 'corresponding' in paper['cv_role'].lower(),'CV selection must show lead authorship')
manuscript_ids=set()
for manuscript in data['manuscripts']:
    for key in ['id','title','authors','venue','status','status_as_of']:
        require(bool(manuscript.get(key)),f'Missing manuscript field: {key}')
    require(manuscript['id'] not in ids | manuscript_ids,'Duplicate manuscript/publication id')
    manuscript_ids.add(manuscript['id'])
    require(manuscript['status'] in ['Under review','Under review following revision','Under review following second revision'],'Invalid review status')
    require(re.fullmatch(r'\d{4}-\d{2}-\d{2}',str(manuscript['status_as_of'])),'Use ISO date for review status')
    if manuscript.get('code'):
        require(manuscript['code'].startswith('https://github.com/'),'Invalid manuscript code link')
    require(manuscript['title'].casefold() not in {p['title'].casefold() for p in data['publications']},'Manuscript duplicated in published work')
for grant in data['funding']:
    require(grant['category'] in ['individual','collaborative'],'Invalid funding category')
    for key in ['title','funder','role','project']:require(bool(grant.get(key)),f'Missing grant field: {key}')
    for key in ['period','details']:require(key in grant,f'Missing grant field: {key}')
for project in data['software']:
    for key in ['name','category','description','tags','links']:require(bool(project.get(key)),f'Missing software field: {key}')
    require(any('github.com/' in x['url'] for x in project['links']),f'Missing repository: {project["name"]}')
require(isinstance(data['profile']['seeking_postdoc'],bool),'seeking_postdoc must be true or false')
poems=[yaml.safe_load(p.read_text(encoding='utf-8').split('---',2)[1]) for p in (ROOT/'_poems').glob('*.md')]
require(len({p['key'] for p in poems})==len(poems),'Poem keys must be globally unique')
poem_urls=set()
for poem in poems:
    for key in ['title','book','order','permalink','verse','chapter','form']:require(bool(poem.get(key)),f'Missing poem field: {key}')
    require(poem['permalink'] not in poem_urls,'Duplicate poem URL')
    poem_urls.add(poem['permalink'])
    require(poem['book'] in [b['id'] for b in data['poetry']['books']],'Unknown poetry collection')
for book in data['poetry']['books']:
    orders=sorted(p['order'] for p in poems if p['book']==book['id'])
    require(orders==list(range(1,len(orders)+1)),f'Non-contiguous poem order: {book["id"]}')
for title in data['poetry']['featured_titles']:require(any(p['title']==title for p in poems),f'Missing featured poem: {title}')
require(sum(p.get('key')==data['poetry'].get('latest_poem') for p in poems)==1,'Latest poem must reference exactly one existing poem key')
for item in data['poetry_cards']['curated']:
    matches=[p for p in poems if p['key']==item['poem']]
    require(len(matches)==1 and item['excerpt'] in matches[0]['verse'],'Card excerpt must match original poem verbatim')
endpoint=data['poetry_cards'].get('realtime_endpoint','')
require(not endpoint or endpoint.startswith('https://'),'Realtime endpoint must be HTTPS')

class Page(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.links=[];self.scripts=[];self.json_mode=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a' and 'href' in a:self.links.append(a['href'])
        if tag in ['img','script','audio','source'] and 'src' in a:self.links.append(a['src'])
        if tag=='link' and a.get('rel') in ['stylesheet','icon']:self.links.append(a['href'])
        if tag=='script':self.json_mode=a.get('type')=='application/ld+json'
    def handle_data(self,text):
        if self.json_mode:self.scripts.append(text)
    def handle_endtag(self,tag):
        if tag=='script':self.json_mode=False

if len(sys.argv)>1:
    build=Path(sys.argv[1])
    targets=['index.html','cv/index.html']+[str(p.relative_to(build)) for p in (build/'poetry').rglob('*.html')]
    require((build/'poetry/index.html').exists(),'Poetry homepage missing')
    library=json.loads((build/'poetry/cards/library.json').read_text(encoding='utf-8'))
    require({p['key']:p['verse'] for p in library}=={p['key']:p['verse'] for p in poems},'Card library must preserve every original poem')
    for target in targets:
        p=Page();html=(build/target).read_text(encoding='utf-8');p.feed(html)
        if target in ['index.html','cv/index.html']:require(not re.search(r'[\u3400-\u9fff]',html),f'Chinese text remains in English academic page: {target}')
        if target.startswith('poetry'):require(not re.search(r'王天龙|Tianlong[ _-]*Wang|Wang[ ,_-]*Tianlong',html,re.I),f'Real name remains in poetry page: {target}')
        require(len(p.ids)==len(set(p.ids)),f'Duplicate HTML ids in {target}')
        require('{{' not in html and '{%' not in html,f'Unrendered template in {target}')
        for script in p.scripts:json.loads(script)
        for href in p.links:
            if href.startswith('#'):require(unquote(href[1:]) in p.ids,f'Broken anchor: {href}')
            elif href.startswith('/') and not href.startswith('//'):
                path=build/unquote(urlparse(href).path).lstrip('/')
                if urlparse(href).path.endswith('/'):path=path/'index.html'
                require(path.exists(),f'Missing asset/page: {href}')
print(f'PASS: {len(ids)} publications, {len(manuscript_ids)} manuscripts, {len(data["funding"])} grants, {len(data["software"])} software projects; selected references valid.')

