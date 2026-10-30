"""Real filesystem installer tests; no agent accounts or home directories used."""
from pathlib import Path
import contextlib,hashlib,importlib.util,io,json,os,stat,sys,tempfile,unittest,zipfile
from unittest.mock import patch
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


if __name__=='__main__':unittest.main()
