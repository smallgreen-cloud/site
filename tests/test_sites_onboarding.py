import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
import yaml
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build import load_onboarding, onboarding_detail_body, onboarding_architecture
from gen_arch_svg import arch_svg

class SitesOnboardingTest(unittest.TestCase):
    def fixture(self):
        bilingual=lambda value:{'en':value,'zh-tw':value}
        return {'id':'fixture-sites','name':'Fixture Sites','state':'evidence-needed','state_label':bilingual('Candidate'),
          'product_summary':{k:bilingual(['fixture'] if k not in ['project_type','problem'] else 'fixture') for k in ['project_type','problem','audience','capabilities','deployment_requirements','limitations']},
          'architecture':{'sites':['site','d1','r2','mcp'],'external_services':[]},'current_stage':bilingual('Candidate'),'next_steps':bilingual(['verify']),
          'source':{'repository':'smallgreen-cloud/petmcp-sites','locked_commit':'a'*40,'license':'MIT'},
          'agent_install':{'protocol':'smallgreen-install/v1','status':'candidate','deployment_ready':False,'target':{'client':'chatgpt-work','hosting':'sites','execution_mode':'native-sites'},
          'contract_url':'https://raw.githubusercontent.com/smallgreen-cloud/petmcp-sites/'+'a'*40+'/.smallgreen/install.yaml',
          'hosting':{'managed_resources':['site','d1','r2'],'external_infrastructure':[]},'trigger':bilingual('Read the pinned install contract and use Sites only.'),
          'steps':bilingual(['Open ChatGPT','Install your own Site PWA']),'privacy':bilingual('Data stays in your Site.'),'blockers':['phone not tested']}}

    def load(self,project):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'onboarding').mkdir();(root/'onboarding/first-party.yaml').write_text(yaml.safe_dump({'projects':[project]}));return load_onboarding(root)

    def test_sites_candidate_renders_locked_source_and_copy_prompt(self):
        p=self.load(self.fixture())[0]
        html=onboarding_detail_body(p,'zh-tw')
        self.assertIn('建立我的 PetMCP' if p['name']=='PetMCP Sites' else '建立我的 Site',html)
        self.assertIn('data-copy=',html)
        self.assertIn(p['agent_install']['contract_url'],html)
        self.assertIn('https://chatgpt.com/',html)
        self.assertIn('Candidate',html)
        self.assertIn('ChatGPT Sites',arch_svg(onboarding_architecture(p)))
        self.assertNotIn('localStorage',html)

    def test_sites_candidate_cannot_claim_ready_or_external_resources(self):
        for key,value in [('status','ready'),('deployment_ready',True),('blockers',[])]:
            p=self.fixture();p['agent_install'][key]=value
            with self.assertRaises(ValueError): self.load(p)
        p=self.fixture();p['agent_install']['hosting']['external_infrastructure']=['cloudflare-account']
        with self.assertRaises(ValueError):self.load(p)

    def test_unpinned_source_and_mixed_cloudflare_are_rejected(self):
        p=self.fixture();p['source']['locked_commit']='main'
        with self.assertRaises(ValueError):self.load(p)
        p=self.fixture();p['architecture']['cloudflare']=['workers']
        with self.assertRaises(ValueError):self.load(p)

if __name__=='__main__':unittest.main()
