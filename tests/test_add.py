import unittest
import mock
from mock import Mock
from tests.ditest import DependencyInjectionTestBase


class AddTests(DependencyInjectionTestBase):

    def setUp(self):
        super(AddTests, self).setUp()
        self.config.dryrun = False
        self.repo.knows.return_value = False
        self.repo.knowsSeries.return_value = False
        self.img = Mock()
        self.fileFactory.locatedAt.return_value = self.img

    def add(self, path, **kwargs):
        from niprov.adding import add
        return add(path, dependencies=self.dependencies, **kwargs)

    def assertNotCalledWith(self, m, *args, **kwargs):
        c = mock.call(*args, **kwargs)
        assert c not in m.call_args_list, "Unexpectedly found call: "+str(c)

    def test_Returns_provenance_and_status(self):
        new = '/p/f2'
        (provenance, status) = self.add(new)
        self.assertEqual(provenance, self.img.provenance)
        self.assertEqual(status, 'new')

    def test_Sets_transient_flag_if_provided(self):
        (provenance, status) = self.add('/p/f1', transient=True)
        self.fileFactory.locatedAt.assert_called_with('/p/f1', 
            provenance={'transient':True})

    def test_Creates_ImageFile_object_with_factory(self):
        (provenance, status) = self.add('p/afile.f')
        self.fileFactory.locatedAt.assert_called_with('p/afile.f', 
            provenance={'transient': False})
        self.assertRaises(AssertionError,
            self.fileFactory.locatedAt.assert_any_call,'root/other.file')

    def test_Calls_inspect(self):
        (provenance, status) = self.add('p/afile.f')
        self.img.inspect.assert_called_with()

    def test_Hands_provenance_to_repository(self):
        (provenance, status) = self.add('p/afile.f')
        self.repo.add.assert_any_call(self.img)

    def test_If_discovers_file_that_is_known_ignore_it(self):
        self.repo.knows.return_value = True
        (provenance, status) = self.add('p/afile.f')
        assert not self.repo.add.called
        self.listener.knownFile.assert_called_with(self.img.path)
        self.assertEqual(status, 'known')

    def test_If_repo_doesnt_know_file_but_knows_series_update_series(self):
        self.repo.knows.return_value = False
        self.repo.knowsSeries.return_value = True
        series = Mock()
        self.repo.getSeries.return_value = series
        (provenance, status) = self.add('p/afile.f')
        series.addFile.assert_called_with(self.img)
        self.repo.update.assert_called_with(series)
        self.listener.fileFoundInSeries.assert_called_with(self.img, series)
        self.assertEqual(status, 'series')

    def test_If_inspect_raises_exceptions_tells_listener_and_doesnt_save(self):
        self.img.inspect.side_effect = IOError
        (provenance, status) = self.add('p/afile.f')
        self.assertNotCalledWith(self.repo.add, self.img)
        self.listener.fileError.assert_called_with(self.img.path)
        self.assertEqual(status, 'failed')

    def test_If_dryrun_doesnt_talk_to_repo_and_status_is_test(self):
        self.config.dryrun = True
        (provenance, status) = self.add('p/afile.f')
        assert not self.repo.add.called
        assert not self.repo.update.called
        assert not self.img.inspect.called
        self.assertEqual(status, 'dryrun')

    def test_accepts_optional_provenance(self):
        (provenance, status) = self.add('p/afile.f', provenance={'fob':'bez'})
        self.fileFactory.locatedAt.assert_called_with('p/afile.f', 
            provenance={'fob':'bez','transient':False})

    def test_If_file_doesnt_exists_tells_listener_and_doesnt_save_prov(self):
        self.filesys.fileExists.return_value = False
        self.assertRaises(IOError, self.add, 'p/afile.f')

    def test_For_nonexisting_transient_file_behaves_normal(self):
        self.filesys.fileExists.return_value = False
        self.add('p/afile.f', transient=True)

    def test_Doesnt_inspect_transient_files(self):
        self.add('p/afile.f', transient=True)
        assert not self.img.inspect.called


