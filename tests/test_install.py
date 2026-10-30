"""Real filesystem installer tests; no agent accounts or home directories used."""
from pathlib import Path
import contextlib,hashlib,importlib.util,io,json,os,stat,sys,tempfile,unittest,zipfile
from unittest.mock import MagicMock,patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('jfk_install',ROOT/'install.py')
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
SOURCE=ROOT/'skills/journal-matplotlib'


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='jfk-test-');self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def target(self,name='skills'):return self.root/name/installer.NAME

    def test_all_agent_paths_and_legacy_codex(self):
        home=self.root/'home';project=self.root/'project'
        for agent,(local,global_,_) in installer.AGENTS.items():
            self.assertEqual(installer.destination(agent,'project',project,home,{}),project/local/installer.NAME)
            self.assertEqual(installer.destination(agent,'user',project,home,{}),home/global_/installer.NAME)
        custom=self.root/'custom'
        self.assertEqual(installer.destination('codex','user',project,home,{'CODEX_HOME':str(custom)}),custom/'skills'/installer.NAME)
        legacy=home/'.codex/skills'/installer.NAME;legacy.mkdir(parents=True)
        self.assertEqual(installer.destination('codex','user',project,home,{}),legacy)

    def test_each_adapter_preserves_workflow_and_resources(self):
        canonical=(SOURCE/'SKILL.md').read_text(encoding='utf-8').split('---',2)[2]
        for agent in installer.AGENTS:
            target=self.target(agent);installer.install_one(SOURCE,target,agent)
            text=(target/'SKILL.md').read_text(encoding='utf-8')
            self.assertEqual(text.split('---',2)[2],canonical)
            self.assertEqual('disable-model-invocation: true' in text,agent in installer.MANUAL_FRONTMATTER)
            self.assertEqual((target/'agents/openai.yaml').exists(),agent in ('codex','generic'))
            self.assertEqual((target/'scripts/layout_audit.py').read_bytes(),(SOURCE/'scripts/layout_audit.py').read_bytes())
            self.assertEqual((target/'LICENSE').read_bytes(),(SOURCE/'LICENSE').read_bytes())

    def test_existing_install_requires_update_and_preserves_files(self):
        target=self.target();installer.install_one(SOURCE,target,'codex')
        note=target/'my-note.txt';note.write_text('Keep me')
        with self.assertRaises(FileExistsError):installer.install_one(SOURCE,target,'codex')
        self.assertEqual(note.read_text(),'Keep me')

    def test_update_backup_and_runtime_preservation(self):
        target=self.target();installer.install_one(SOURCE,target,'codex',python=sys.executable)
        (target/'my-note.txt').write_text('Local edit')
        result=installer.install_one(SOURCE,target,'codex',update=True)
        with zipfile.ZipFile(result['backup']) as z:self.assertEqual(z.read(installer.NAME+'/my-note.txt'),b'Local edit')
        self.assertEqual(json.loads((target/'local_runtime.json').read_text())['python'],sys.executable)
        self.assertFalse((target/'my-note.txt').exists())

    def test_failed_replace_restores_original(self):
        target=self.target();installer.install_one(SOURCE,target,'codex');(target/'note').write_text('original')
        original=Path.rename
        def fail_payload(path,dest):
            if path.name==installer.NAME and '.journal-figure-kit-stage-' in str(path.parent):raise OSError('simulated rename failure')
            return original(path,dest)
        with patch.object(Path,'rename',fail_payload),self.assertRaises(OSError):installer.install_one(SOURCE,target,'codex',update=True)
        self.assertEqual((target/'note').read_text(),'original')

    def test_symlink_target_rejected(self):
        outside=self.root/'outside';outside.mkdir();target=self.target();target.parent.mkdir()
        try:target.symlink_to(outside,target_is_directory=True)
        except OSError:self.skipTest('OS does not permit test symlinks')
        with self.assertRaises(ValueError):installer.install_one(SOURCE,target,'codex',update=True)
        self.assertEqual(list(outside.iterdir()),[])

    def test_dry_run_has_no_writes_or_downloads(self):
        with patch.object(installer,'download') as network,contextlib.redirect_stdout(io.StringIO()):
            result=installer.main(['--agent','claude-code','--dest',str(self.root/'new'),'--dry-run','--with-deps'])
        self.assertEqual(result,0);self.assertFalse((self.root/'new').exists());network.assert_not_called()

    def test_conflicts_are_checked_before_any_agent_is_installed(self):
        blocked=self.root/'.cursor/skills'/installer.NAME;blocked.mkdir(parents=True)
        with contextlib.redirect_stdout(io.StringIO()),self.assertRaises(FileExistsError):
            installer.main(['--agent','claude-code','cursor','--project',str(self.root),'--source',str(SOURCE)])
        self.assertFalse((self.root/'.claude').exists())

    def test_no_dependency_install_without_opt_in(self):
        with patch.object(installer,'runtime_environment') as runtime,contextlib.redirect_stdout(io.StringIO()):
            installer.main(['--agent','gemini','--dest',str(self.root/'new'),'--source',str(SOURCE)])
        runtime.assert_not_called()

    def test_runtime_keeps_virtual_environment_interpreter(self):
        env=self.root/'figure env'
        installer.venv.EnvBuilder(with_pip=False,symlinks=os.name!='nt').create(env)
        with patch.object(installer.subprocess,'run') as pip:
            python=installer.runtime_environment(env,SOURCE/'requirements.txt')
        pip.assert_called_once()
        result=installer.subprocess.run([python,'-c','import sys; print(sys.prefix)'],capture_output=True,text=True,check=True)
        self.assertEqual(Path(result.stdout.strip()).resolve(),env.resolve())

    def test_incomplete_source_and_version_mismatch_rejected(self):
        with self.assertRaises(ValueError):installer.validate_source(self.root)
        target=self.target();installer.install_one(SOURCE,target,'codex');(target/'VERSION').write_text('0.0')
        with self.assertRaises(ValueError):installer.validate_source(target)

    def test_archive_traversal_duplicates_and_symlinks_rejected(self):
        for names in [['../outside'],[installer.NAME+'/../../outside'],['C:/outside'],[installer.NAME+'\\outside'],[installer.NAME+'/A',installer.NAME+'/a']]:
            buffer=io.BytesIO()
            with zipfile.ZipFile(buffer,'w') as z:
                for name in names:
                    entry=zipfile.ZipInfo();entry.filename=name;entry.orig_filename=name
                    z.writestr(entry,'x')
            with self.subTest(names=names),self.assertRaises(ValueError):installer.extract_skill(buffer.getvalue(),self.root)
        buffer=io.BytesIO();entry=zipfile.ZipInfo(installer.NAME+'/link');entry.external_attr=(stat.S_IFLNK|0o777)<<16
        with zipfile.ZipFile(buffer,'w') as z:z.writestr(entry,'outside')
        with self.assertRaises(ValueError):installer.extract_skill(buffer.getvalue(),self.root)
        self.assertEqual(list(self.root.iterdir()),[])

    def test_download_checksum_mismatch_rejected(self):
        fake=self.root/'install.py';fake.write_text('standalone')
        asset=f'journal-figure-kit-{installer.VERSION}-skill.zip'
        with patch.object(installer,'__file__',str(fake)),patch.object(installer,'download',side_effect=[('0'*64+'  '+asset+'\n').encode(),b'bad']),self.assertRaises(ValueError):
            with installer.source_tree():pass

    def test_downloaded_release_validated_before_install(self):
        data=io.BytesIO()
        with zipfile.ZipFile(data,'w') as z:
            for p in installer.files(SOURCE):z.write(p,installer.NAME+'/'+p.relative_to(SOURCE).as_posix())
        raw=data.getvalue();asset=f'journal-figure-kit-{installer.VERSION}-skill.zip'
        fake=self.root/'install.py';fake.write_text('standalone')
        with patch.object(installer,'__file__',str(fake)),patch.object(installer,'download',side_effect=[(hashlib.sha256(raw).hexdigest()+'  '+asset+'\n').encode(),raw]):
            with installer.source_tree() as source:
                self.assertEqual((source/'VERSION').read_text().strip(),installer.VERSION)

    def test_memory_and_stdin_bootstrap_use_pinned_release(self):
        data=io.BytesIO()
        with zipfile.ZipFile(data,'w') as z:
            for p in installer.files(SOURCE):z.write(p,installer.NAME+'/'+p.relative_to(SOURCE).as_posix())
        raw=data.getvalue();asset=f'journal-figure-kit-{installer.VERSION}-skill.zip'
        checksums=(hashlib.sha256(raw).hexdigest()+'  '+asset+'\n').encode()
        for filename in (None,'<stdin>'):
            with self.subTest(filename=filename),patch.object(installer,'__file__',filename),patch.object(installer,'download',side_effect=[checksums,raw]) as network:
                with installer.source_tree() as source:
                    self.assertNotEqual(source,SOURCE)
                    self.assertEqual((source/'VERSION').read_text().strip(),installer.VERSION)
                self.assertEqual(network.call_count,2)

    def test_memory_and_stdin_entrypoints_install_without_script_file(self):
        source=(ROOT/'install.py').read_text(encoding='utf-8')
        for mode in ('memory','stdin'):
            args=[sys.executable,'-c',source] if mode=='memory' else [sys.executable,'-']
            dest=self.root/mode
            args+=['--agent','claude-code','--dest',str(dest),'--source',str(SOURCE)]
            with self.subTest(mode=mode):
                result=installer.subprocess.run(args,input=source if mode=='stdin' else None,capture_output=True,text=True,cwd=self.root)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual((dest/installer.NAME/'VERSION').read_text().strip(),installer.VERSION)
                self.assertFalse((self.root/'install.py').exists())

    def test_transient_download_errors_retry_with_a_limit(self):
        response=MagicMock();response.__enter__.return_value.read.return_value=b'ok'
        errors=[installer.http.client.RemoteDisconnected('closed'),installer.urllib.error.HTTPError('https://example.invalid',503,'busy',{},None)]
        with patch.object(installer.urllib.request,'urlopen',side_effect=errors+[response]) as network,patch.object(installer.time,'sleep') as pause:
            self.assertEqual(installer.download('https://example.invalid',100),b'ok')
            self.assertEqual(network.call_count,3);self.assertEqual(pause.call_count,2)
        with patch.object(installer.urllib.request,'urlopen',side_effect=TimeoutError('timeout')) as network,patch.object(installer.time,'sleep'),self.assertRaises(TimeoutError):
            installer.download('https://example.invalid',100)
        self.assertEqual(network.call_count,3)

    def test_permanent_download_failures_are_not_retried(self):
        error=installer.urllib.error.HTTPError('https://example.invalid',404,'missing',{},None)
        with patch.object(installer.urllib.request,'urlopen',side_effect=error) as network,self.assertRaises(installer.urllib.error.HTTPError):
            installer.download('https://example.invalid',100)
        self.assertEqual(network.call_count,1)
        response=MagicMock();response.__enter__.return_value.read.return_value=b'too long'
        with patch.object(installer.urllib.request,'urlopen',return_value=response) as network,self.assertRaises(ValueError):
            installer.download('https://example.invalid',2)
        self.assertEqual(network.call_count,1)

    def test_check_detects_modified_install(self):
        target=self.target();installer.install_one(SOURCE,target,'codex',python=sys.executable)
        self.assertTrue(installer.check_install(target)['ok'])
        (target/'SKILL.md').write_text('changed')
        self.assertFalse(installer.check_install(target)['ok'])

    def test_unicode_and_spaces_in_target(self):
        target=self.target('科研 图 安装');installer.install_one(SOURCE,target,'cursor')
        self.assertTrue((target/'references/agent-usage.md').is_file())

    def test_bundled_requirements_match_repository(self):
        def deps(p):return [x.strip() for x in p.read_text().splitlines() if x.strip() and not x.startswith('#')]
        self.assertEqual(deps(ROOT/'requirements.txt'),deps(SOURCE/'requirements.txt'))

    def test_quick_defaults_and_explicit_project(self):
        for extra,agent,scope in [([], 'codex','user'),(['--agent','cursor','--project',str(self.root)],'cursor','project')]:
            output=io.StringIO()
            with self.subTest(scope=scope),patch.dict(os.environ,{},clear=True),patch.object(Path,'home',return_value=self.root/'home'),contextlib.redirect_stdout(output):
                self.assertEqual(installer.main(['--quick','--dry-run']+extra),0)
            record=json.loads(output.getvalue())[0]
            self.assertEqual(record['agent'],agent);self.assertTrue(record['with_deps'])
            expected=installer.destination(agent,scope,self.root,self.root/'home',{})
            self.assertEqual(Path(record['target']),expected)

    def test_quick_update_backs_up_existing_install(self):
        target=self.target();installer.install_one(SOURCE,target,'codex')
        (target/'note').write_text('keep in backup')
        with contextlib.redirect_stdout(io.StringIO()),patch.object(installer,'runtime_environment') as runtime:
            self.assertEqual(installer.main(['--quick','--no-deps','--dest',str(target.parent)]),0)
        runtime.assert_not_called()
        backups=list((target.parent/'.journal-figure-kit-backups').glob('*.zip'))
        self.assertEqual(len(backups),1)
        with zipfile.ZipFile(backups[0]) as z:self.assertEqual(z.read(installer.NAME+'/note'),b'keep in backup')

    def test_quick_no_update_refuses_existing_install(self):
        target=self.target();installer.install_one(SOURCE,target,'codex')
        with self.assertRaises(FileExistsError):
            installer.main(['--quick','--no-deps','--no-update','--dest',str(target.parent)])

    def test_quick_check_does_not_install_or_update(self):
        target=self.target();installer.install_one(SOURCE,target,'codex',python=sys.executable)
        with patch.object(installer,'source_tree') as source,patch.object(installer,'runtime_environment') as runtime,contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(installer.main(['--quick','--dest',str(target.parent),'--check']),0)
        source.assert_not_called();runtime.assert_not_called()
        self.assertFalse((target.parent/'.journal-figure-kit-backups').exists())

    def test_quick_dependency_setup_uses_selected_environment(self):
        target=self.target();runtime_path=self.root/'figure env'
        with patch.object(installer,'runtime_environment',return_value=sys.executable) as runtime,contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(installer.main(['--quick','--dest',str(target.parent),'--venv',str(runtime_path)]),0)
        runtime.assert_called_once_with(runtime_path,SOURCE/'requirements.txt')
        self.assertEqual(json.loads((target/'local_runtime.json').read_text())['python'],sys.executable)


if __name__=='__main__':unittest.main()
