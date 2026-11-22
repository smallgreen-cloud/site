"""Sites candidate handoff rendered exclusively from Registry metadata."""
import re
from html import escape

def validate_sites_onboarding(project):
    architecture = project['architecture']
    install = project.get('agent_install', {})
    source = project.get('source', {})
    def require(condition, message):
        if not condition:
            raise ValueError(f"onboarding project {project['id']}: {message}")
    require(architecture.get('sites') == ['site', 'd1', 'r2', 'mcp'], 'requires Sites-managed site/d1/r2/mcp')
    require(not architecture.get('cloudflare') and not architecture.get('external_services'), 'cannot mix external infrastructure into Sites-only')
    require(install.get('protocol') == 'smallgreen-install/v1', 'unsupported install protocol')
    require(install.get('status') == 'candidate' and install.get('deployment_ready') is False, 'candidate cannot claim ready')
    require(install.get('target') == {'client':'chatgpt-work','hosting':'sites','execution_mode':'native-sites'}, 'requires native Sites')
    require(install.get('hosting') == {'managed_resources':['site','d1','r2'],'external_infrastructure':[]}, 'requires only Sites-managed resources')
    require(isinstance(install.get('blockers'), list) and bool(install['blockers']), 'candidate needs blockers')
    repo = source.get('repository','')
    require(bool(re.fullmatch(r'[\w.-]+/[\w.-]+', repo)), 'invalid repository')
    require(bool(re.fullmatch(r'[0-9a-f]{40}', source.get('locked_commit',''))), 'source must pin a commit')
    require(bool(source.get('license')), 'license required')
    require(bool(re.fullmatch(r'https://raw\.githubusercontent\.com/'+re.escape(repo)+r'/[0-9a-f]{40}/\.smallgreen/install\.yaml', install.get('contract_url',''))), 'contract must pin a commit')
    for field in ['trigger','steps','privacy']:
        require(isinstance(install.get(field),dict) and all(install[field].get(lang) for lang in ['en','zh-tw']), f'{field} must be bilingual')
    require(all(isinstance(install['steps'][lang],list) for lang in ['en','zh-tw']), 'steps must be lists')

def sites_install_body(project, lang):
    install = project.get('agent_install')
    if not install:
        return ''
    source = project['source']
    label = install.get('cta',{}).get(lang, '建立我的 Site' if lang == 'zh-tw' else 'Create my Site')
    command_id = 'sites-install-' + project['id']
    steps = ''.join(f'<li>{escape(str(step))}</li>' for step in install['steps'][lang])
    blockers = ''.join(f'<li>{escape(str(item))}</li>' for item in install['blockers'])
    note = ('需具備 Sites 權限的 ChatGPT 方案；資格、建置與 AI 額度以帳號當下顯示為準。公開 Site 可讀不代表免費帳號可自行建立。'
            if lang == 'zh-tw' else 'A ChatGPT plan with Sites access is required. Eligibility, build and AI quotas depend on the current account. Public viewing does not imply free-account creation access.')
    return f'''<section class="agent-install candidate-install"><h2>{escape(label)}</h2>
<p><span class="onboarding-state">Candidate · evidence-needed</span></p><p>{note}</p>
<p><a href="https://github.com/{escape(source['repository'])}">GitHub · {escape(source['license'])}</a> · <a href="https://github.com/{escape(source['repository'])}/tree/{source['locked_commit']}">{'鎖定來源' if lang=='zh-tw' else 'Pinned source'} {source['locked_commit'][:12]}</a></p>
<div class="command"><code id="{command_id}">{escape(install['trigger'][lang])}</code><button class="copy-button" type="button" data-copy="{command_id}" data-copied-label="{'已複製' if lang=='zh-tw' else 'Copied'}">{'複製部署提示' if lang=='zh-tw' else 'Copy deployment prompt'}</button></div>
<p><a href="https://chatgpt.com/" target="_blank" rel="noreferrer">{'開啟 ChatGPT 並使用 Sites' if lang=='zh-tw' else 'Open ChatGPT and use Sites'}</a> · <a href="{escape(install['contract_url'])}">{'讀取安裝契約' if lang=='zh-tw' else 'Read install contract'}</a> · <a href="/services/{escape(project['id'])}/install.json">install.json</a></p>
<ol>{steps}</ol><h3>{'隱私與個人入口' if lang=='zh-tw' else 'Privacy and personal access'}</h3><p>{escape(install['privacy'][lang])}</p>
<h3>{'尚待驗收' if lang=='zh-tw' else 'Remaining acceptance'}</h3><ul>{blockers}</ul></section>'''
