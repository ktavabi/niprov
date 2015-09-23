from mock import Mock
from tests.ditest import DependencyInjectionTestBase


class JsonFileTest(DependencyInjectionTestBase):

    def setUp(self):
        super(JsonFileTest, self).setUp()
        self.dependencies.getConfiguration().database_url = ''

    def test_Update(self):
        from niprov.jsonfile import JsonFile
        repo = JsonFile(self.dependencies)
        repo._all = Mock()
        repo._all.return_value = [{'location':'1','path':'a'},
            {'location':'2','path':'b'}]
        image = Mock()
        image.location.toString.return_value = '2'
        image.provenance = {'foo':'bar'}
        repo.update(image)
        self.serializer.serializeList.assert_called_with(
            [{'location':'1','path':'a'},{'foo':'bar'}])
        self.filesys.write.assert_called_with(repo.datafile, 
            self.serializer.serializeList())

    def test_Add(self):
        from niprov.jsonfile import JsonFile
        repo = JsonFile(self.dependencies)
        repo._all = Mock()
        repo._all.return_value = [{'location':'1','path':'a'}]
        image = Mock()
        image.provenance = {'foo':'bar'}
        repo.add(image)
        self.serializer.serializeList.assert_called_with(
            [{'location':'1','path':'a'},{'foo':'bar'}])
        self.filesys.write.assert_called_with(repo.datafile, 
            self.serializer.serializeList())

    def test_knowsByLocation(self):
        from niprov.jsonfile import JsonFile
        repo = JsonFile(self.dependencies)
        repo.byLocation = Mock()
        self.assertTrue(repo.knowsByLocation(''))
        repo.byLocation.side_effect = IndexError
        self.assertFalse(repo.knowsByLocation(''))

    def test_byLocation(self):
        from niprov.jsonfile import JsonFile
        repo = JsonFile(self.dependencies)
        repo._all = Mock()
        repo._all.return_value = [{'location':'1','path':'a'},
            {'location':'2','path':'b'}]
        out = repo.byLocation('1')
        self.fileFactory.fromProvenance.assert_called_with(
            {'location':'1','path':'a'})
        self.assertEqual(self.fileFactory.fromProvenance(), out)

    def test_byLocation_works_for_file_in_series(self):
        from niprov.jsonfile import JsonFile
        repo = JsonFile(self.dependencies)
        repo._all = Mock()
        repo._all.return_value = [{'location':'1','path':'a'},
            {'location':'3','filesInSeries':['boo','bah']}]
        out = repo.byLocation('boo')
        self.fileFactory.fromProvenance.assert_called_with(
            {'location':'3','filesInSeries':['boo','bah']})
        self.assertEqual(self.fileFactory.fromProvenance(), out)

    def test_updateApproval(self):
        from niprov.jsonfile import JsonFile
        repo = JsonFile(self.dependencies)
        img = Mock()
        img.provenance = {'fiz':'baf','approval':'notsure'}
        def assertion(img):
            self.assertEqual({'fiz':'baf','approval':'excellent!'}, img.provenance)
        repo.byLocation = Mock()
        repo.byLocation.return_value = img
        repo.update = Mock()
        repo.update.side_effect = assertion
        repo.updateApproval('/p/f1','excellent!')

    def test_bySubject(self):
        self.fileFactory.fromProvenance.side_effect = lambda p: 'img_'+p['a']
        from niprov.jsonfile import JsonFile
        repo = JsonFile(self.dependencies)
        repo._all = Mock()
        repo._all.return_value = [{'subject':'john','a':'b'},
            {'subject':'tim','a':'d'},{'subject':'john','a':'f'}]
        out = repo.bySubject('john')
        self.fileFactory.fromProvenance.assert_any_call({'subject':'john','a':'b'})
        self.fileFactory.fromProvenance.assert_any_call({'subject':'john','a':'f'})
        self.assertEqual(['img_b', 'img_f'], out)

    def test_byApproval(self):
        self.fileFactory.fromProvenance.side_effect = lambda p: 'img_'+p['a']
        from niprov.jsonfile import JsonFile
        repo = JsonFile(self.dependencies)
        repo._all = Mock()
        repo._all.return_value = [{'approval':'y','a':'b'},
            {'approval':'x','a':'d'},{'approval':'x','a':'f'}]
        out = repo.byApproval('x')
        self.fileFactory.fromProvenance.assert_any_call({'approval':'x','a':'d'})
        self.fileFactory.fromProvenance.assert_any_call({'approval':'x','a':'f'})
        self.assertEqual(['img_d', 'img_f'], out)

        
        

