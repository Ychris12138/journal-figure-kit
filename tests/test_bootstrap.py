"""Exercise real shell processes without network or changes to a user's skills."""
from pathlib import Path
import json,os,shutil,subprocess,sys,tempfile,unittest

ROOT=Path(__file__).resolve().parents[1]
VERSION=(ROOT/'skills/journal-matplotlib/VERSION').read_text().strip()

def shells():
    found=[]
    for name in ('powershell.exe','pwsh'):
        executable=shutil.which(name)
        if executable:found.append(('ps',executable))
    if os.name=='nt':
        git=shutil.which('git')
        bash=Path(git).resolve().parent.parent/'bin/bash.exe' if git else None
        if bash and bash.is_file():found.append(('bash',str(bash)))
    else:
        bash='/bin/bash' if sys.platform=='darwin' and Path('/bin/bash').is_file() else shutil.which('bash')
        if bash:found.append(('bash',bash))
    return found

def ps_quote(value):return "'"+str(value).replace("'","''")+"'"

class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='jfk-shell-')
        self.root=Path(self.tmp.name)
        self.stub=self.root/'backend with spaces.py'
        self.stub.write_text("import json,os,sys\nfrom pathlib import Path\nPath(os.environ['JFK_TEST_OUTPUT']).write_text(json.dumps(sys.argv[1:]))\nsys.exit(int(os.environ.get('JFK_TEST_EXIT','0')))\n",encoding='utf-8')
        self.output=self.root/'arguments.json'
        self.env={**os.environ,'JFK_PYTHON':Path(sys.executable).as_posix(),'JFK_INSTALLER':self.stub.as_posix(),
                  'JFK_TEST_OUTPUT':str(self.output),'PYTHONUTF8':'1'}
        self.hosts=shells()
        if not self.hosts:self.skipTest('No supported shell is available')

    def tearDown(self):self.tmp.cleanup()

    def invoke(self,host,args=(),pipe=False,extra_env=None):
        kind,shell=host
        env={**self.env,**(extra_env or {})}
        script=ROOT/('install.ps1' if kind=='ps' else 'install.sh')
        if kind=='ps':
            if pipe:
                code=f'Get-Content -LiteralPath {ps_quote(script)} -Raw | Invoke-Expression'
            else:
                code=f'& ([scriptblock]::Create([IO.File]::ReadAllText({ps_quote(script)}))) '+ ' '.join(ps_quote(a) for a in args)
            command=[shell,'-NoProfile','-NonInteractive','-Command',code];input_=None
        else:
            command=[shell] if pipe else [shell,script.as_posix(),*map(str,args)]
            input_=script.read_text(encoding='utf-8') if pipe else None
        return subprocess.run(command,input=input_,capture_output=True,text=True,encoding='utf-8',errors='replace',env=env,cwd=self.root,timeout=45)

    def test_pipe_entry_forwards_quick_mode(self):
        for host in self.hosts:
            with self.subTest(host=host):
                result=self.invoke(host,pipe=True)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                self.assertEqual(json.loads(self.output.read_text()),['--quick'])

    def test_arguments_and_paths_with_spaces_are_preserved(self):
        args=['--agent','claude-code','--project',str(self.root/'space folder'),'--no-deps','--no-update']
        for host in self.hosts:
            with self.subTest(host=host):
                result=self.invoke(host,args)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                self.assertEqual(json.loads(self.output.read_text()),['--quick',*args])

    def test_python_is_detected_without_an_override(self):
        env={'JFK_PYTHON':'','PATH':str(Path(sys.executable).parent)+os.pathsep+os.environ.get('PATH','')}
        for host in self.hosts:
            with self.subTest(host=host):
                result=self.invoke(host,pipe=True,extra_env=env)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                self.assertEqual(json.loads(self.output.read_text()),['--quick'])

    def test_backend_failure_is_nonzero(self):
        for host in self.hosts:
            with self.subTest(host=host):
                result=self.invoke(host,pipe=True,extra_env={'JFK_TEST_EXIT':'29'})
                self.assertNotEqual(result.returncode,0,result.stdout+result.stderr)

    def test_missing_python_fails_before_backend(self):
        for host in self.hosts:
            with self.subTest(host=host):
                result=self.invoke(host,pipe=True,extra_env={'JFK_PYTHON':str(self.root/'missing-python')})
                self.assertNotEqual(result.returncode,0)
                self.assertFalse(self.output.exists())

    def test_real_local_install_and_check(self):
        for index,host in enumerate(self.hosts):
            with self.subTest(host=host):
                dest=self.root/f'figure skills {index}'
                env={'JFK_INSTALLER':(ROOT/'install.py').as_posix()}
                result=self.invoke(host,['--agent','claude-code','--dest',str(dest),'--no-deps','--no-update'],extra_env=env)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                skill=dest/'journal-matplotlib'
                self.assertEqual((skill/'VERSION').read_text().strip(),VERSION)
                self.assertIn('disable-model-invocation: true',(skill/'SKILL.md').read_text(encoding='utf-8'))
                result=self.invoke(host,['--agent','claude-code','--dest',str(dest),'--check'],extra_env=env)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                self.assertIn('"ok": true',result.stdout)

    def test_powershell_failure_can_be_caught_without_exiting_host(self):
        for kind,shell in self.hosts:
            if kind!='ps':continue
            code=f"try {{ Get-Content -LiteralPath {ps_quote(ROOT/'install.ps1')} -Raw | Invoke-Expression }} catch {{ Write-Output 'HOST_STILL_RUNNING' }}"
            result=subprocess.run([shell,'-NoProfile','-NonInteractive','-Command',code],env={**self.env,'JFK_TEST_EXIT':'29'},capture_output=True,text=True,errors='replace',timeout=30)
            self.assertIn('HOST_STILL_RUNNING',result.stdout,result.stderr)

    def test_wrappers_pin_matching_backend_version(self):
        for filename in ('install.ps1','install.sh'):
            text=(ROOT/filename).read_text(encoding='ascii')
            self.assertIn("'"+VERSION+"'",text)
            self.assertIn('raw.githubusercontent.com/Ychris12138/journal-figure-kit/v',text)

if __name__=='__main__':unittest.main()
