"""Behavior tests with synthetic data; test confirmations are not user approval."""
from pathlib import Path
import contextlib
import copy
import io
import json
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT/'skills/journal-matplotlib/scripts'
sys.path.insert(0, str(SCRIPTS))
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, NumberObject
import palette_cards as cards
import palette_audit as audit
import figure_export as exports
import inspect_outputs as inspector


def options(**kwargs):
    base = dict(mode='publication', tolerance_mm=.25, dpi=600, background='#FFFFFF',
                white_threshold=8, margin_mm=4, margin_fraction=.05,
                min_font_pt=None, max_font_pt=None, raster_dpi=None)
    return SimpleNamespace(**(base | kwargs))


def result():
    return {'warnings': [], 'errors': []}


class PaletteTests(unittest.TestCase):
    def setUp(self):
        self.deck = cards.load_deck(ROOT/'skills/journal-matplotlib/references/shi-tanaka-cards.json')
        self.approval = cards.confirm(self.deck, 'D', 'SYNTHETIC TEST ONLY', 'unit test only')

    def test_pending_cannot_export(self):
        with self.assertRaises(ValueError):
            cards.approved_settings(self.deck, {'status': 'pending'})

    def test_matching_confirmation_reusable(self):
        for _ in range(2):
            self.assertEqual(cards.approved_settings(self.deck, self.approval)['mapping'], self.deck['cards'][0]['mapping'])

    def test_encoding_changes_invalidate_confirmation(self):
        changes = [lambda c: c['mapping'].__setitem__('Group 1', '#123456'),
                   lambda c: c.__setitem__('mapping', dict(reversed(list(c['mapping'].items())))),
                   lambda c: c['mapping'].__setitem__('New state', c['mapping'].pop('Group 1')),
                   lambda c: c.__setitem__('band_alpha', .3),
                   lambda c: c.__setitem__('revision', 3)]
        for change in changes:
            revised = copy.deepcopy(self.deck)
            change(revised['cards'][0])
            with self.subTest(card=revised['cards'][0]), self.assertRaises(ValueError):
                cards.approved_settings(revised, self.approval)

    def test_tampered_confirmation_rejected(self):
        self.approval['card']['text'] = '#000000'
        with self.assertRaises(ValueError):
            cards.approved_settings(self.deck, self.approval)

    def test_blank_reply_rejected(self):
        with self.assertRaises(ValueError):
            cards.confirm(self.deck, 'D', ' ', 'test')

    def test_duplicate_colors_rejected(self):
        card = self.deck['cards'][0]
        card['mapping']['Group 2'] = card['mapping']['Group 1']
        with self.assertRaises(ValueError):
            cards.validate_card(card)

    def test_numeric_norm_and_approval(self):
        card = copy.deepcopy(self.deck['cards'][0]); card.pop('mapping')
        card.update(kind='diverging', colors=['#0022AA', '#FFFFFF', '#BB2200'],
                    normalization=dict(vmin=-2, vmax=3, center=0, scale='linear', units='a.u.', missing_color='#777777'))
        deck = {'schema_version': 1, 'cards': [card]}
        cards.validate_card(card)
        approved = cards.confirm(deck, 'D', 'SYNTHETIC TEST ONLY', 'test')
        card['normalization']['vmax'] = 4
        with self.assertRaises(ValueError):
            cards.approved_settings(deck, approved)
        card['normalization']['center'] = 5
        with self.assertRaises(ValueError):
            cards.validate_card(card)

    def test_invalid_log_and_cyclic_maps(self):
        card = copy.deepcopy(self.deck['cards'][0]); card.pop('mapping')
        card.update(kind='sequential', colors=['#0022AA', '#FFFFFF'],
                    normalization=dict(vmin=0, vmax=3, scale='log', units='a.u.', missing_color='#777777'))
        with self.assertRaises(ValueError):
            cards.validate_card(card)
        card.update(kind='cyclic');card['normalization']['scale']='linear'
        with self.assertRaises(ValueError):
            cards.validate_card(card)

    def test_contrast_reference_values(self):
        self.assertAlmostEqual(audit.contrast((0, 0, 0), (1, 1, 1)), 21)
        self.assertAlmostEqual(audit.contrast((1, 1, 1), (1, 1, 1)), 1)

    def test_gray_preserves_luminance(self):
        for value in ('#E20D0D', '#0402DB', '#010101', '#FE9301'):
            original = audit.rgb(value)
            self.assertAlmostEqual(audit.luminance(original), audit.luminance(audit.gray(original)), places=7)

    def test_screen_does_not_modify_or_approve(self):
        before = copy.deepcopy(self.deck)
        with tempfile.TemporaryDirectory() as directory:
            report = audit.audit(self.deck, directory, cvd=False)
            self.assertEqual(report['status'], 'review_only')
            self.assertIn('CVD disabled by caller', report['skipped'])
            self.assertEqual(self.deck, before)
            self.assertFalse((Path(directory)/'approval.json').exists())

    def test_cvd_all_three_finite(self):
        for kind in ('deuteranomaly', 'protanomaly', 'tritanomaly'):
            values, _ = audit.simulate([(1, 0, 0), (0, 1, 0), (0, 0, 1)], kind)
            self.assertTrue(np.isfinite(values).all())
            self.assertTrue(np.all((np.array(values) >= 0) & (np.array(values) <= 1)))


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.stem = Path(self.directory.name)/'figure'
        self.fig, self.ax = plt.subplots(figsize=(89/25.4, 65/25.4), layout='constrained')
        self.ax.plot([0, 1, 2], [0, 1, .5], label='Synthetic')
        self.ax.set(xlabel='Distance (nm)', ylabel='Response')

    def tearDown(self):
        plt.close('all'); self.directory.cleanup()

    def export(self, **kwargs):
        return exports.export_pair(self.fig, self.stem, width_mm=89, height_mm=65, **kwargs)

    def test_global_tight_crop_cannot_change_canvas_or_leak_style(self):
        with mpl.rc_context({'savefig.bbox': 'tight', 'pdf.fonttype': 3}):
            self.export()
            self.assertEqual(mpl.rcParams['savefig.bbox'], 'tight')
            self.assertEqual(mpl.rcParams['pdf.fonttype'], 3)
        page = PdfReader(str(self.stem)+'.pdf').pages[0]
        self.assertAlmostEqual(float(page.mediabox.width)*25.4/72, 89, places=5)
        self.assertAlmostEqual(float(page.mediabox.height)*25.4/72, 65, places=5)
        with Image.open(str(self.stem)+'.png') as image:
            self.assertAlmostEqual(image.width*25.4/image.info['dpi'][0], 89, delta=.05)
        self.assertTrue(Path(str(self.stem)+'.export.json').is_file())

    def test_wrong_contract_rejected_before_writing(self):
        with self.assertRaises(ValueError):
            exports.export_pair(self.fig, self.stem, width_mm=90, height_mm=65)
        self.assertEqual(list(Path(self.directory.name).iterdir()), [])

    def test_invalid_dpi_rejected(self):
        for dpi in (0, float('nan'), True):
            with self.assertRaises(ValueError):
                self.export(dpi=dpi)

    def test_overwrite_requires_explicit_flag(self):
        self.export()
        with self.assertRaises(FileExistsError):
            self.export()
        self.export(overwrite=True)

    def test_render_failure_leaves_no_published_pair(self):
        original = self.fig.savefig
        def fail_png(path, **kwargs):
            if path.suffix == '.png':
                raise RuntimeError('Synthetic render failure')
            return original(path, **kwargs)
        with patch.object(self.fig, 'savefig', side_effect=fail_png), self.assertRaises(RuntimeError):
            self.export()
        self.assertEqual(list(Path(self.directory.name).iterdir()), [])

    def test_off_canvas_annotation_detected(self):
        self.fig.text(1.05, .5, 'Off canvas', in_layout=False)
        self.assertTrue(any('figure_text' in s for s in exports.layout_warnings(self.fig)))

    def test_data_and_missing_gap_preserved(self):
        y = np.array([1., .5, np.nan, .2])
        line, = self.ax.plot(np.arange(4), y)
        self.export()
        np.testing.assert_equal(line.get_ydata(), y)
        self.assertTrue(np.isnan(line.get_path().vertices[2, 1]))

    def test_exported_pdf_has_text_and_vector_paths(self):
        import pymupdf
        self.export()
        with pymupdf.open(str(self.stem)+'.pdf') as pdf:
            self.assertIn('Distance', pdf[0].get_text())
            self.assertTrue(pdf[0].get_drawings())
            self.assertNotIn('Type3', str(pdf[0].get_fonts()))


class InspectorTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
    def tearDown(self):
        self.directory.cleanup()

    def test_nonwhite_margin_measurement(self):
        path = self.root/'gray.png'
        image = Image.new('RGB', (100, 80), '#EEEEEE')
        ImageDraw.Draw(image).rectangle((10, 8, 89, 71), fill='black')
        image.save(path, dpi=(100, 100))
        report = result()
        inspector.inspect_png(path, report, options(dpi=100, background='#EEEEEE'), (None, None))
        margins = report['png']['outer_margins_fraction']
        self.assertEqual(margins, dict(left=.1, top=.1, right=.1, bottom=.1))

    def test_blank_background_is_error(self):
        path = self.root/'blank.png'; Image.new('RGB', (20, 20), '#EEEEEE').save(path, dpi=(100, 100))
        report = result()
        inspector.inspect_png(path, report, options(background='#EEEEEE'), (None, None))
        self.assertIn('blank_image', [v['code'] for v in report['errors']])

    def test_large_border_is_warning_not_auto_crop(self):
        path = self.root/'padding.png'; image = Image.new('RGB', (100, 100), 'white')
        ImageDraw.Draw(image).rectangle((30, 30, 70, 70), fill='black'); image.save(path, dpi=(100, 100))
        before = path.read_bytes(); report = result()
        inspector.inspect_png(path, report, options(dpi=100), (None, None))
        self.assertIn('outer_whitespace', [v['code'] for v in report['warnings']])
        self.assertEqual(path.read_bytes(), before)

    def test_missing_dpi_fails_exact_size_check(self):
        path = self.root/'no-dpi.png'; Image.new('RGB', (20, 20), 'black').save(path)
        report = result()
        inspector.inspect_png(path, report, options(), (89, 65))
        self.assertIn('unverifiable_size', [v['code'] for v in report['errors']])

    def test_pdf_userunit_in_physical_size(self):
        writer = PdfWriter(); page = writer.add_blank_page(width=100, height=100)
        page[NameObject('/UserUnit')] = NumberObject(2)
        path = self.root/'unit.pdf'; writer.write(path)
        report = result(); inspector.inspect_pdf(path, report, options(), (None, None))
        self.assertAlmostEqual(report['pdf']['size_mm'][0][0], 200*25.4/72)

    def test_missing_pair_is_error(self):
        report = inspector.inspect_stem(self.root/'absent', options())
        self.assertEqual(len(report['errors']), 2)

    def test_missing_dependency_reported_as_skip(self):
        import builtins
        original = builtins.__import__
        def blocked(name, *args, **kwargs):
            if name == 'PIL':
                raise ImportError('synthetic missing dependency')
            return original(name, *args, **kwargs)
        report = result()
        with patch('builtins.__import__', side_effect=blocked):
            inspector.inspect_png(self.root/'unused.png', report, options(), (89, 65))
        self.assertIn('skipped_png', [v['code'] for v in report['warnings']])

    def test_bad_background_cli_rejected(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            inspector.main([str(self.root/'absent'), '--background', 'not-a-color'])
        self.assertEqual(caught.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
