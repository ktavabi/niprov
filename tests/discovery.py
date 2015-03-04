import unittest
import mock
from mock import Mock
import os.path as ospath

class DiscoveryTests(unittest.TestCase):

    def setUp(self):
        self.repo = Mock()
        self.repo.knows.return_value = False
        self.img1 = Mock()
        self.img2 = Mock()
        self.img3 = Mock()
        self.fileFactory = Mock()
        self.fileFactory.locatedAt.side_effect = [self.img1, self.img2, self.img3]
        self.filesys = Mock()
        self.filesys.walk.return_value = [('root',[],['known','new','unknown'])]
        self.listener = Mock()
        self.filt = Mock()
        self.inspect = Mock()
        self.inspect.side_effect = lambda x: ('p', x)

    def discover(self, path):
        import niprov.discovery
        niprov.discovery.inspect = self.inspect
        niprov.discovery.discover(path, filesys=self.filesys, listener=self.listener,
            filefilter=self.filt, repository=self.repo, file=self.fileFactory)

    def test_Tells_listener_about_files_found(self):
        self.setupFilter('.x')
        self.filesys.walk.return_value = [('root',[],['/p/f1.x','/p/f2.x']),
            ('root',[],['/p/p2/f3.x'])] #(dirpath, dirnames, filenames)
        self.discover('root')
        self.filesys.walk.assert_called_with('root')
        self.listener.fileFound.assert_any_call(self.img1)
        self.listener.fileFound.assert_any_call(self.img2)
        self.listener.fileFound.assert_any_call(self.img3)

    def test_file_filters(self):
        self.setupFilter('valid.file')
        self.filesys.walk.return_value = [('root',[],['valid.file','other.file'])]
        self.discover('root')
        self.listener.fileFound.assert_any_call(self.img1)

    def test_Creates_ImageFile_object_with_factory(self):
        self.setupFilter('.valid')
        self.filesys.walk.return_value = [('root',[],['a.valid', 'other.file'])]
        self.discover('root')
        self.fileFactory.locatedAt.assert_any_call('root/a.valid')
        self.assertRaises(AssertionError,
            self.fileFactory.locatedAt.assert_any_call,'root/other.file')

    def test_Calls_inspect(self):
        self.setupFilter('.valid')
        self.filesys.walk.return_value = [('root',[],['a.valid','b.valid'])]
        self.discover('root')
        self.img1.inspect.assert_called_with()

    def test_Hands_provenance_to_repository(self):
        self.setupFilter('.valid')
        self.filesys.walk.return_value = [('root',[],['a.valid','other.file','b.valid'])]
        self.discover('root')
        self.repo.add.assert_any_call(self.img1.provenance)
        self.repo.add.assert_any_call(self.img2.provenance)

    def test_If_discovers_file_that_is_known_ignore_it(self):
        self.repo.knows.side_effect = lambda f: True if f==self.img2 else False
        self.discover('root')
        self.repo.add.assert_any_call(self.img1.provenance)
        self.assertNotCalledWith(self.repo.add, self.img2.provenance)
        self.listener.knownFile.assert_called_with(self.img2.path)

    def assertNotCalledWith(self, m, *args, **kwargs):
        c = mock.call(*args, **kwargs)
        assert c not in m.call_args_list, "Unexpectedly found call: "+str(c)

    def setupFilter(self, valid):
        def filter_side_effect(*args):
            if valid in args[0]:
                return True
            return False
        self.filt.include = Mock(side_effect=filter_side_effect)
        

