import unittest2 as unittest
from ftw.mobilenavigation.testing import MOBILE_NAVIGATION_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import login, setRoles


class TestView(unittest.TestCase):

    layer = MOBILE_NAVIGATION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.portal.invokeFactory(id='f1', type_name='Folder')

    def test_level_0(self):
        # level 0 loads the global navigation
        self.portal.REQUEST.form.update({'level': '0'})
        self.assertEqual(
            self.portal.unrestrictedTraverse('load_children')(),
            '<ul id="portal-globalnav" class="mobileNavigation"><li class="noChildren level0"><a href="http://nohost/plone/f1"></a></li></ul>')

    def test_portal_link(self):
        # if the object is the portal and its not level 0 there should not be returned anything.
        self.portal.REQUEST.form.update({'level': '1'})
        self.assertEqual(
            self.portal.unrestrictedTraverse('load_children')(),
            '<ul></ul>')

    def test_subfolder(self):
        # if there is a subfolder show a link to toggle children
        self.portal.f1.invokeFactory(id='subfolder1', type_name='Folder')
        self.portal.REQUEST.form.update({'level': '0'})
        self.assertEqual(
            self.portal.unrestrictedTraverse('load_children')(),
            '<ul id="portal-globalnav" class="mobileNavigation"><li class="level0"><a href="http://nohost/plone/f1"></a></li></ul>')

    def test_subfolder_hidden(self):
        # No link to toggle children if there are just objects not listed in navigation
        self.portal.f1.invokeFactory(id='file1', type_name='File')
        self.portal.REQUEST.form.update({'level': '0'})
        ptool = getToolByName(self.portal, 'portal_properties')
        ptool.navtree_properties.metaTypesNotToList = ('File')
        self.assertEqual(
            self.portal.unrestrictedTraverse('load_children')(),
            '<ul id="portal-globalnav" class="mobileNavigation"><li class="noChildren level0"><a href="http://nohost/plone/f1"></a></li></ul>')

    def test_subfolder_excluded(self):
        # No link to toggle children if the subfolder is excluded from navigation
        self.portal.f1.invokeFactory(id='subfolder1', type_name='Folder')
        self.portal.f1.subfolder1.setExcludeFromNav(True)
        self.portal.f1.subfolder1.reindexObject()
        self.portal.REQUEST.form.update({'level': '0'})
        self.assertEqual(
            self.portal.unrestrictedTraverse('load_children')(),
            '<ul id="portal-globalnav" class="mobileNavigation"><li class="noChildren level0"><a href="http://nohost/plone/f1"></a></li></ul>')

    def test_level_3(self):
        # create a folder and a subfolder on portal
        self.portal.f1.invokeFactory(id='folder1', type_name='Folder')
        self.portal.f1.folder1.invokeFactory(id='subfolder1', type_name='Folder')
        # level 1 => has children => show link
        self.portal.REQUEST.form.update({'level': '1'})
        self.assertEqual(
            self.portal.f1.unrestrictedTraverse('load_children')(),
            '<ul><li class="level1"><a href="http://nohost/plone/f1/folder1"></a></li></ul>')
        # level 3 => has children => dont show link
        self.portal.REQUEST.form.update({'level': '3'})
        self.assertEqual(
            self.portal.f1.unrestrictedTraverse('load_children')(),
            '<ul><li class="noChildren level3"><a href="http://nohost/plone/f1/folder1"></a></li></ul>')
