# -*- coding: utf-8 -*-
# Stalker a Production Asset Management System
# Copyright (C) 2009-2013 Erkan Ozgur Yilmaz
# 
# This file is part of Stalker.
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation;
# version 2.1 of the License.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

import unittest2
from stalker import (Link, Project, Repository, Sequence, Shot, Status,
                     StatusList, Task, Type, Version, FilenameTemplate, Structure)
from stalker import db
from stalker.db.session import DBSession, ZopeTransactionExtension

from stalker import config
from stalker.exceptions import CircularDependencyError

defaults = config.Config()

import logging
from stalker import log

logger = logging.getLogger('stalker.models.version.Version')
logger.setLevel(log.logging_level)


class VersionTester(unittest2.TestCase):
    """tests stalker.models.version.Version class
    """

    @classmethod
    def setUpClass(cls):
        """setting up the test in class level
        """
        DBSession.remove()
        DBSession.configure(extension=None)

    @classmethod
    def tearDownClass(cls):
        """clean up the test in class level
        """
        DBSession.remove()
        DBSession.configure(extension=ZopeTransactionExtension)

    def setUp(self):
        """setup the test
        """
        DBSession.remove()
        db.setup()

        # statuses
        self.test_status1 = Status(name='Status1', code='STS1')
        self.test_status2 = Status(name='Status2', code='STS2')
        self.test_status3 = Status(name='Status3', code='STS3')
        self.test_status4 = Status(name='Status4', code='STS4')
        self.test_status5 = Status(name='Status5', code='STS5')

        # status lists
        self.test_project_status_list = StatusList(
            name='Project Status List',
            statuses=[
                self.test_status1,
                self.test_status2,
                self.test_status3,
                self.test_status4,
                self.test_status5,
            ],
            target_entity_type=Project,
        )

        self.test_sequence_status_list = StatusList(
            name='Sequence Status List',
            statuses=[
                self.test_status1,
                self.test_status2,
                self.test_status3,
                self.test_status4,
                self.test_status5,
            ],
            target_entity_type=Sequence,
        )

        self.test_shot_status_list = StatusList(
            name='Shot Status List',
            statuses=[
                self.test_status1,
                self.test_status2,
                self.test_status3,
                self.test_status4,
                self.test_status5,
            ],
            target_entity_type=Shot,
        )

        self.test_task_status_list = StatusList(
            name='Task Status List',
            statuses=[
                self.test_status1,
                self.test_status2,
                self.test_status3,
                self.test_status4,
                self.test_status5,
            ],
            target_entity_type=Task,
        )

        self.test_version_status_list = StatusList(
            name='Version Status List',
            statuses=[
                self.test_status1,
                self.test_status2,
                self.test_status3,
                self.test_status4,
                self.test_status5,
            ],
            target_entity_type=Version,
        )

        # repository
        self.test_repo = Repository(
            name='Test Repository',
            linux_path='/mnt/T/',
            windows_path='T:/',
            osx_path='/Volumes/T/'
        )

        # a project type
        self.test_project_type = Type(
            name='Test',
            code='test',
            target_entity_type=Project,
        )
        
        # create a structure
        self.test_structure = Structure(
            name='Test Project Structure'
        )

        # create a project
        self.test_project = Project(
            name='Test Project',
            code='tp',
            type=self.test_project_type,
            status_list=self.test_project_status_list,
            repository=self.test_repo,
            structure=self.test_structure
        )

        # create a sequence
        self.test_sequence = Sequence(
            name='Test Sequence',
            code='SEQ1',
            project=self.test_project,
            status_list=self.test_sequence_status_list,
        )

        # create a shot
        self.test_shot1 = Shot(
            name='SH001',
            code='SH001',
            project=self.test_project,
            sequences=[self.test_sequence],
            status_list=self.test_shot_status_list,
        )

        # create a group of Tasks for the shot
        self.test_task1 = Task(
            name='Task1',
            parent=self.test_shot1,
            status_list=self.test_task_status_list,
        )

        # a Link for the input file
        self.test_input_link1 = Link(
            name='Input Link 1',
            full_path='/mnt/M/JOBs/TestProj/Seqs/TestSeq/Shots/SH001/FX/'
                      'Outputs/SH001_beauty_v001.###.exr'
        )

        self.test_input_link2 = Link(
            name='Input Link 2',
            full_path='/mnt/M/JOBs/TestProj/Seqs/TestSeq/Shots/SH001/FX/'
                      'Outputs/SH001_occ_v001.###.exr'
        )

        # a Link for the output file
        self.test_output_link1 = Link(
            name='Output Link 1',
            full_path='/mnt/M/JOBs/TestProj/Seqs/TestSeq/Shots/SH001/FX/'
                      'Outputs/SH001_beauty_v001.###.exr'
        )

        self.test_output_link2 = Link(
            name='Output Link 2',
            full_path='/mnt/M/JOBs/TestProj/Seqs/TestSeq/Shots/SH001/FX/'
                      'Outputs/SH001_occ_v001.###.exr'
        )

        # now create a version for the Task
        self.kwargs = {
            'name': 'Version1',
            'take_name': 'TestTake',
            'inputs': [self.test_input_link1,
                       self.test_input_link2],
            'outputs': [self.test_output_link1,
                        self.test_output_link2],
            'task': self.test_task1,
            'status_list': self.test_version_status_list,
        }
        
        self.take_name_test_values = [
            ('Take Name', 'Take_Name'),
            ('TakeName', 'TakeName'),
            ('take name', 'take_name'),
            ('  take_name', 'take_name'),
            ('take_name   ', 'take_name'),
            ('   take   name   ', 'take_name'),
            ('TakeName', 'TakeName')
        ]

        # and the Version
        self.test_version = Version(**self.kwargs)

        # set the published to False
        self.test_version.is_published = False

    def tearDown(self):
        """clean up test
        """
        DBSession.remove()

    def test___auto_name__class_attribute_is_set_to_True(self):
        """testing if the __auto_name__ class attribute is set to True for
        Version class
        """
        self.assertTrue(Version.__auto_name__)

    def test_take_name_argument_is_skipped_defaults_to_default_value(self):
        """testing if the take_name argument is skipped the take attribute is
        going to be set to the default value which is
        stalker.conf.defaults.DEFAULT_VERSION_TAKE_NAME
        """
        self.kwargs.pop('take_name')
        new_version = Version(**self.kwargs)
        self.assertEqual(new_version.take_name,
                         defaults.version_take_name)

    def test_take_name_argument_is_None(self):
        """testing if a TypeError will be raised when the take_name argument is
        None
        """
        self.kwargs['take_name'] = None
        self.assertRaises(TypeError, Version, **self.kwargs)

    def test_take_name_attribute_is_None(self):
        """testing if a TypeError will be raised when the take_name attribute
        is set to None
        """
        self.assertRaises(TypeError, setattr, self.test_version, 'take_name',
                          None)

    def test_take_name_argument_is_empty_string(self):
        """testing if a ValueError will be raised when the take_name argument
        is given as an empty string
        """
        self.kwargs['take_name'] = ''
        self.assertRaises(ValueError, Version, **self.kwargs)

    def test_take_name_attribute_is_empty_string(self):
        """testing if a ValueError will be raised when the take_name attribute
        is set to an empty string
        """
        self.assertRaises(ValueError, setattr, self.test_version, 'take_name',
                          '')

    def test_take_name_argument_is_not_a_string_will_be_converted_to_one(self):
        """testing if the given take_name argument is not a string will be
        converted to a proper string
        """
        test_values = [
            (1, '1'),
            (1.2, '12'),
            (['a list'], 'a_list'),
            ({'a': 'dict'}, 'a_dict')]

        for test_value in test_values:
            self.kwargs['take_name'] = test_value[0]
            new_version = Version(**self.kwargs)

            self.assertEqual(new_version.take_name, test_value[1])

    def test_take_name_attribute_is_not_a_string_will_be_converted_to_one(
            self):
        """testing if the given take_name attribute is not a string will be
        converted to a proper string
        """
        test_values = [
            (1, '1'),
            (1.2, '12'),
            (['a list'], 'a_list'),
            ({'a': 'dict'}, 'a_dict')]

        for test_value in test_values:
            self.test_version.take_name = test_value[0]
            self.assertEqual(self.test_version.take_name, test_value[1])

    def test_take_name_argument_is_formatted_to_empty_string(self):
        """testing if a ValueError will be raised when the take_name argument
        string is formatted to an empty string
        """
        self.kwargs['take_name'] = '##$½#$'
        self.assertRaises(ValueError, Version, **self.kwargs)

    def test_take_name_attribute_is_formatted_to_empty_string(self):
        """testing if a ValueError will be raised when the take_name argument
        string is formatted to an empty string
        """
        self.assertRaises(ValueError, setattr, self.test_version, 'take_name',
                          '##$½#$')

    def test_take_name_argument_is_formatted_correctly(self):
        """testing if the take_name argument value is formatted correctly
        """
        for test_value in self.take_name_test_values:
            self.kwargs['take_name'] = test_value[0]
            new_version = Version(**self.kwargs)
            self.assertEqual(
                new_version.take_name,
                test_value[1]
            )

    def test_take_name_attribute_is_formatted_correctly(self):
        """testing if the take_name attribute value is formatted correctly
        """
        for test_value in self.take_name_test_values:
            self.test_version.take_name = test_value[0]
            self.assertEqual(
                self.test_version.take_name,
                test_value[1]
            )

    def test_task_argument_is_skipped(self):
        """testing if a TypeError will be raised when the task argument
        is skipped
        """
        self.kwargs.pop('task')
        self.assertRaises(TypeError, Version, **self.kwargs)

    def test_task_argument_is_None(self):
        """testing if a TypeError will be raised when the task argument
        is None
        """
        self.kwargs['task'] = None
        self.assertRaises(TypeError, Version, **self.kwargs)

    def test_task_attribute_is_None(self):
        """testing if a TypeError will be raised when the task attribute
        is None
        """
        self.assertRaises(TypeError, setattr, self.test_version,
                          'task', None)

    def test_task_argument_is_not_a_Task(self):
        """testing if a TypeError will be raised when the task argument
        is not a Task instance
        """
        self.kwargs['task'] = 'a task'
        self.assertRaises(TypeError, Version, **self.kwargs)

    def test_task_attribute_is_not_a_Task(self):
        """testing if a TypeError will be raised when the task attribute
        is not a Task instance
        """
        self.assertRaises(TypeError, setattr, self.test_version, 'task',
                          'a task')

    def test_task_attribute_is_working_properly(self):
        """testing if the task attribute is working properly
        """
        new_task = Task(
            name='New Test Task',
            parent=self.test_shot1,
            status_list=self.test_task_status_list,
        )

        self.assertIsNot(self.test_version.task, new_task)
        self.test_version.task = new_task
        self.assertIs(self.test_version.task, new_task)

    def test_version_number_attribute_is_automatically_generated(self):
        """testing if the version_number attribute is automatically generated
        """
        self.assertEqual(self.test_version.version_number, 1)
        DBSession.add(self.test_version)
        DBSession.commit()

        new_version = Version(**self.kwargs)
        DBSession.add(new_version)
        DBSession.commit()

        self.assertEqual(self.test_version.task, new_version.task)
        self.assertEqual(self.test_version.take_name, new_version.take_name)

        self.assertEqual(new_version.version_number, 2)

    def test_version_number_attribute_is_starting_from_1(self):
        """testing if the version_number attribute is starting from 1
        """
        self.assertEqual(self.test_version.version_number, 1)

    def test_version_number_attribute_is_set_to_a_lower_then_it_should_be(
            self):
        """testing if the version_number attribute will be set to a correct
        unique value when it is set to a lower number then it should be
        """

        self.test_version.version_number = -1
        self.assertEqual(self.test_version.version_number, 1)

        self.test_version.version_number = -10
        self.assertEqual(self.test_version.version_number, 1)

        DBSession.add(self.test_version)
        DBSession.commit()

        self.test_version.version_number = -100
        # it should be 1 again
        self.assertEqual(self.test_version.version_number, 1)

        new_version = Version(**self.kwargs)
        self.assertEqual(new_version.version_number, 2)

        new_version.version_number = 1
        self.assertEqual(new_version.version_number, 2)

        new_version.version_number = 100
        self.assertEqual(new_version.version_number, 100)

    # def test_source_file_argument_is_skipped(self):
    #     """testing if the source_file will be None when the source_file
    #     argument is skipped
    #     """
    #     self.kwargs.pop('source_file')
    #     new_version = Version(**self.kwargs)
    #     self.assertIs(new_version.source_file, None)
    # 
    # def test_source_file_argument_is_None(self):
    #     """testing if the source_file will be None when the source argument is
    #     None
    #     """
    #     self.kwargs['source_file'] = None
    #     new_version = Version(**self.kwargs)
    #     self.assertIs(new_version.source_file, None)
    # 
    # def test_source_file_argument_is_not_a_Link_instance(self):
    #     """testing if a TypeError will be raised when the source_file argument
    #     is not a stalker.models.link.Link instance
    #     """
    #     self.kwargs['source_file'] = 123123
    #     self.assertRaises(TypeError, Version, **self.kwargs)
    # 
    # def test_source_file_attribute_is_not_a_Link_instance(self):
    #     """testing if a TypeError will be raised when the source_file attribute
    #     is set to something other than a Link instance
    #     """
    #     self.assertRaises(TypeError, setattr, self.test_version, 'source_file',
    #                       121)
    # 
    # def test_source_file_argument_is_working_properly(self):
    #     """testing if the source_file argument is working properly
    #     """
    #     new_source_file = Link(name='Test Link', full_path='none')
    #     self.kwargs['source_file'] = new_source_file
    #     new_version = Version(**self.kwargs)
    #     self.assertEqual(new_version.source_file, new_source_file)
    # 
    # def test_source_file_attribute_is_working_properly(self):
    #     """testing if the source_file attribute is working properly
    #     """
    #     new_source_file = Link(name='Test Link', full_path='empty string')
    #     self.assertNotEqual(self.test_version.source_file, new_source_file)
    #     self.test_version.source_file = new_source_file
    #     self.assertEqual(self.test_version.source_file, new_source_file)

    def test_inputs_argument_is_skipped(self):
        """testing if the inputs attribute will be an empty list when the
        inputs argument is skipped
        """
        self.kwargs.pop('inputs')
        new_version = Version(**self.kwargs)
        self.assertEqual(new_version.inputs, [])

    def test_inputs_argument_is_None(self):
        """testing if the inputs attribute will be an empty list when the
        inputs argument is None
        """
        self.kwargs['inputs'] = None
        new_version = Version(**self.kwargs)
        self.assertEqual(new_version.inputs, [])

    def test_inputs_attribute_is_None(self):
        """testing if a TypeError will be raised when the inputs argument is
        set to None
        """
        self.assertRaises(TypeError, setattr, self.test_version, 'inputs',
                          None)

    def test_inputs_argument_is_not_a_list_of_Link_instances(self):
        """testing if a TypeError will be raised when the inputs attribute is
        set to something other than a Link instance
        """
        test_value = [132, '231123']
        self.kwargs['inputs'] = test_value
        self.assertRaises(TypeError, Version, **self.kwargs)

    def test_inputs_attribute_is_not_a_list_of_Link_instances(self):
        """testing if a TypeError will be raised when the inputs attribute is
        set to something other than a Link instance
        """
        test_value = [132, '231123']
        self.assertRaises(TypeError, setattr, self.test_version, 'inputs',
                          test_value)

    def test_inputs_attribute_is_working_properly(self):
        """testing if the inputs attribute is working properly
        """
        self.kwargs.pop('inputs')
        new_version = Version(**self.kwargs)

        self.assertNotIn(self.test_input_link1, new_version.inputs)
        self.assertNotIn(self.test_input_link2, new_version.inputs)

        new_version.inputs = [self.test_input_link1, self.test_input_link2]

        self.assertIn(self.test_input_link1, new_version.inputs)
        self.assertIn(self.test_input_link2, new_version.inputs)

    def test_outputs_argument_is_skipped(self):
        """testing if the outputs attribute will be an empty list when the
        outputs argument is skipped
        """
        self.kwargs.pop('outputs')
        new_version = Version(**self.kwargs)
        self.assertEqual(new_version.outputs, [])

    def test_outputs_argument_is_None(self):
        """testing if the outputs attribute will be an empty list when the
        outputs argument is None
        """
        self.kwargs['outputs'] = None
        new_version = Version(**self.kwargs)
        self.assertEqual(new_version.outputs, [])

    def test_outputs_attribute_is_None(self):
        """testing if a TypeError will be raised when the outputs argument is
        set to None
        """
        self.assertRaises(TypeError, setattr, self.test_version, 'outputs',
                          None)

    def test_outputs_argument_is_not_a_list_of_Link_instances(self):
        """testing if a TypeError will be raised when the outputs attribute is
        set to something other than a Link instance
        """
        test_value = [132, '231123']
        self.kwargs['outputs'] = test_value
        self.assertRaises(TypeError, Version, **self.kwargs)

    def test_outputs_attribute_is_not_a_list_of_Link_instances(self):
        """testing if a TypeError will be raised when the outputs attribute is
        set to something other than a Link instance
        """
        test_value = [132, '231123']
        self.assertRaises(TypeError, setattr, self.test_version, 'outputs',
                          test_value)

    def test_outputs_attribute_is_working_properly(self):
        """testing if the outputs attribute is working properly
        """
        self.kwargs.pop('outputs')
        new_version = Version(**self.kwargs)

        self.assertNotIn(self.test_output_link1, new_version.outputs)
        self.assertNotIn(self.test_output_link2, new_version.outputs)

        new_version.outputs = [self.test_output_link1, self.test_output_link2]

        self.assertIn(self.test_output_link1, new_version.outputs)
        self.assertIn(self.test_output_link2, new_version.outputs)

    def test_is_published_attribute_is_False_by_default(self):
        """testing if the is_published attribute is False by default
        """
        self.assertEqual(self.test_version.is_published, False)

    def test_is_published_attribute_is_working_properly(self):
        """testing if the is_published attribute is working properly
        """
        self.test_version.is_published = True
        self.assertEqual(self.test_version.is_published, True)

        self.test_version.is_published = False
        self.assertEqual(self.test_version.is_published, False)

    def test_parent_argument_is_skipped(self):
        """testing if the parent attribute will be None if the parent argument
        is skipped
        """
        try:
            self.kwargs.pop('parent')
        except KeyError:
            pass
        new_version = Version(**self.kwargs)
        self.assertIsNone(new_version.parent)

    def test_parent_argument_is_None(self):
        """testing if the parent attribute will be None if the parent argument
        is skipped
        """
        self.kwargs['parent'] = None
        new_version = Version(**self.kwargs)
        self.assertIsNone(new_version.parent)

    def test_parent_attribute_is_None(self):
        """testing if the parent attribute value will be None if it is set to
        None
        """
        self.test_version.parent = None
        self.assertIsNone(self.test_version.parent)

    def test_parent_argument_is_not_a_Version_instance(self):
        """testing if a TypeError will be raised when the parent argument is
        not a Version instance
        """
        self.kwargs['parent'] = 'not a version instance'
        self.assertRaises(TypeError, Version, **self.kwargs)

    def test_parent_attribute_is_not_set_to_a_Version_instance(self):
        """testing if a TypeError will be raised when the parent attribute is
        not set to a Version instance
        """
        self.assertRaises(TypeError, setattr, self.test_version, 'parent',
                          'not a version instance')

    def test_parent_argument_is_working_properly(self):
        """testing if the parent argument is working properly
        """
        self.kwargs['parent'] = self.test_version
        new_version = Version(**self.kwargs)
        self.assertEqual(new_version.parent, self.test_version)

    def test_parent_attribute_is_working_properly(self):
        """testing if the parent attribute is working properly
        """
        self.kwargs['parent'] = None
        new_version = Version(**self.kwargs)
        self.assertNotEqual(new_version.parent, self.test_version)
        new_version.parent = self.test_version
        self.assertEqual(new_version.parent, self.test_version)

    def test_parent_argument_updates_the_children_attribute(self):
        """testing if the parent argument updates the children attribute of the
        parent Version properly
        """
        self.kwargs['parent'] = self.test_version
        new_version = Version(**self.kwargs)
        self.assertIn(new_version, self.test_version.children)

    def test_parent_attribute_updates_the_children_attribute(self):
        """testing if the parent attribute updates the children attribute of
        the parent Version properly
        """
        self.kwargs['parent'] = None
        new_version = Version(**self.kwargs)
        self.assertNotEqual(new_version.parent, self.test_version)
        new_version.parent = self.test_version
        self.assertIn(new_version, self.test_version.children)

    def test_parent_attribute_will_not_allow_circular_dependencies(self):
        """testing if a CircularDependency will be raised when the given
        Version to the parent attribute is a children of the current Version
        """
        self.kwargs['parent'] = self.test_version
        version1 = Version(**self.kwargs)
        self.assertRaises(CircularDependencyError, setattr, self.test_version,
                          'parent', version1)

    def test_parent_attribute_will_not_allow_deeper_circular_dependencies(
            self):
        """testing if a CircularDependency will be raised when the given
        Version is a parent of the current parent
        """
        self.kwargs['parent'] = self.test_version
        version1 = Version(**self.kwargs)

        self.kwargs['parent'] = version1
        version2 = Version(**self.kwargs)

        # now create circular dependency
        self.assertRaises(CircularDependencyError, setattr, self.test_version,
                          'parent', version2)

    def test_children_attribute_is_set_to_None(self):
        """testing if a TypeError will be raised when the children attribute is
        set to None
        """
        self.assertRaises(TypeError, setattr, self.test_version, 'children',
                          None)

    def test_children_attribute_is_not_set_to_a_list(self):
        """testing if a TypeError will be raised when the children attribute is
        not set to a list
        """
        self.assertRaises(TypeError, setattr, self.test_version, 'children',
                          'not a list of Version instances')

    def test_children_attribute_is_not_set_to_a_list_of_Version_instances(
            self):
        """testing if a TypeError will be raised when the children attribute is
        not set to a list of Version instances
        """
        self.assertRaises(TypeError, setattr, self.test_version, 'children',
                          ['not a Version instance', 3])

    def test_children_attribute_is_working_properly(self):
        """testing if the children attribute is working properly
        """
        self.kwargs['parent'] = None
        new_version1 = Version(**self.kwargs)
        self.test_version.children = [new_version1]
        self.assertIn(new_version1, self.test_version.children)

        new_version2 = Version(**self.kwargs)
        self.test_version.children.append(new_version2)
        self.assertIn(new_version2, self.test_version.children)

    def test_children_attribute_updates_parent_attribute(self):
        """testing if the children attribute updates the parent attribute of
        the children Versions
        """
        self.kwargs['parent'] = None
        new_version1 = Version(**self.kwargs)
        self.test_version.children = [new_version1]
        self.assertEqual(new_version1.parent, self.test_version)

        new_version2 = Version(**self.kwargs)
        self.test_version.children.append(new_version2)
        self.assertEqual(new_version2.parent, self.test_version)

    def test_children_attribute_will_not_allow_circular_dependencies(self):
        """testing if a CircularDependency error will be raised when a parent
        Version is set as a children to its child
        """
        self.kwargs['parent'] = None
        new_version1 = Version(**self.kwargs)
        new_version2 = Version(**self.kwargs)

        new_version1.parent = new_version2
        self.assertRaises(CircularDependencyError,
                          new_version1.children.append, new_version2)

    def test_children_attribute_will_not_allow_deeper_circular_dependencies(
            self):
        """testing if a CircularDependency error will be raised when the a
        parent Version of a parent Version is set as a children to its grand
        child
        """
        self.kwargs['parent'] = None
        new_version1 = Version(**self.kwargs)
        new_version2 = Version(**self.kwargs)
        new_version3 = Version(**self.kwargs)

        new_version1.parent = new_version2
        new_version2.parent = new_version3

        self.assertRaises(CircularDependencyError,
                          new_version1.children.append, new_version3)

    def test_update_paths_will_render_the_appropriate_template_from_the_related_project(
            self):
        """testing if update_paths method will update the Version.full_path by
        rendering the related Project FilenameTemplate.
        """
        # create a FilenameTemplate for Task instances

        # A Template for Assets
        # ......../Assets/{{asset.type.name}}/{{asset.nice_name}}/{{task.type.name}}/
        # 
        # Project1/Assets/Character/Sero/Modeling/Sero_Modeling_Main_v001.ma
        #
        # + Project1
        # |
        # +-+ Assets (Task)
        # | |
        # | +-+ Characters
        # |   |
        # |   +-+ Sero (Asset)
        # |     |
        # |     +-> Version 1
        # |     |
        # |     +-+ Modeling (Task)
        # |       |
        # |       +-+ Body Modeling (Task)
        # |         |
        # |         +-+ Coarse Modeling (Task)
        # |         | |
        # |         | +-> Version 1 (Version)
        # |         |
        # |         +-+ Fine Modeling (Task)
        # |           |
        # |           +-> Version 1 (Version): Fine_Modeling_Main_v001.ma
        # |                                  Assets/Sero/Modeling/Body_Modeling/Fine_Modeling/Fine_Modeling_Main_v001.ma
        # |
        # +-+ Shots (Task)
        #   |
        #   +-+ Shot 10 (Shot)
        #   | |
        #   | +-+ Layout (Task)
        #   |   |
        #   |   +-> Version 1 (Version): Layout_v001.ma
        #   |                            Shots/Shot_1/Layout/Layout_Main_v001.ma
        #   |
        #   +-+ Shot 2 (Shot)
        #     |
        #     +-+ FX (Task)
        #       |
        #       +-> Version 1 (Version)

        ft = FilenameTemplate(
            name='Task Filename Template',
            target_entity_type='Task',
            path='{{project.code}}/{%- for parent_task in parent_tasks -%}{{parent_task.nice_name}}/{%- endfor -%}',
            filename='{{task.nice_name}}_{{version.take_name}}_v{{"%03d"|format(version.version_number)}}{{extension}}',
        )
        self.test_project.structure.templates.append(ft)
        new_version1 = Version(**self.kwargs)
        DBSession.add(new_version1)
        DBSession.commit()
        new_version1.update_paths()

        self.assertEqual(
            new_version1.path,
            'tp/SH001/Task1'
        )

        new_version1.extension = '.ma'
        self.assertEqual(
            new_version1.filename,
            'Task1_TestTake_v001.ma'
        )

    def test_update_paths_will_raise_a_RuntimeError_if_there_is_no_suitable_FilenameTemplate(
            self):
        """testing if update_paths method will raise a RuntimeError if there is
        no suitable FilenameTemplate instance found
        """
        self.kwargs['parent'] = None
        new_version1 = Version(**self.kwargs)
        self.assertRaises(RuntimeError, new_version1.update_paths)

    def test_template_variables_project(self):
        """testing if the project in template variables is correct
        """
        kwargs = self.test_version._template_variables()
        self.assertEqual(
            kwargs['project'],
            self.test_version.task.project
        )

    def test_template_variables_sequences(self):
        """testing if the sequences in template variables is correct
        """
        kwargs = self.test_version._template_variables()
        self.assertEqual(
            kwargs['sequences'],
            []
        )

    def test_template_variables_scenes(self):
        """testing if the scenes in template variables is correct
        """
        kwargs = self.test_version._template_variables()
        self.assertEqual(
            kwargs['scenes'],
            []
        )

    def test_template_variables_shot(self):
        """testing if the shot in template variables is correct
        """
        kwargs = self.test_version._template_variables()
        self.assertEqual(
            kwargs['shot'],
            self.test_version.task
        )

    def test_template_variables_asset(self):
        """testing if the asset in template variables is correct
        """
        kwargs = self.test_version._template_variables()
        self.assertEqual(
            kwargs['asset'],
            self.test_version.task
        )

    def test_template_variables_task(self):
        """testing if the task in template variables is correct
        """
        kwargs = self.test_version._template_variables()
        self.assertEqual(
            kwargs['task'],
            self.test_version.task
        )

    def test_template_variables_parent_tasks(self):
        """testing if the parent_tasks in template variables is correct
        """
        kwargs = self.test_version._template_variables()
        parents = self.test_version.task.parents
        parents.append(self.test_version.task)
        self.assertEqual(
            kwargs['parent_tasks'],
            parents
        )

    def test_template_variables_version(self):
        """testing if the version in template variables is correct
        """
        kwargs = self.test_version._template_variables()
        self.assertEqual(
            kwargs['version'],
            self.test_version
        )

    def test_template_variables_type(self):
        """testing if the type in template variables is correct
        """
        kwargs = self.test_version._template_variables()
        self.assertEqual(
            kwargs['type'],
            self.test_version.type
        )

    def test_absolute_full_path_works_properly(self):
        """testing if the absolute_full_path attribute works properly
        """
        ft = FilenameTemplate(
            name='Task Filename Template',
            target_entity_type='Task',
            path='{{project.code}}/{%- for parent_task in parent_tasks -%}{{parent_task.nice_name}}/{%- endfor -%}',
            filename='{{task.nice_name}}_{{version.take_name}}_v{{"%03d"|format(version.version_number)}}{{extension}}',
        )
        self.test_project.structure.templates.append(ft)
        new_version1 = Version(**self.kwargs)
        DBSession.add(new_version1)
        DBSession.commit()

        new_version1.update_paths()
        new_version1.extension = '.ma'
        self.assertEqual(new_version1.extension, '.ma')

        self.assertEqual(
            new_version1.absolute_full_path,
            '/mnt/T/tp/SH001/Task1/Task1_TestTake_v001.ma'
        )

    def test_absolute_full_path_works_properly(self):
        """testing if the absolute_full_path attribute works properly
        """
        ft = FilenameTemplate(
            name='Task Filename Template',
            target_entity_type='Task',
            path='{{project.code}}/{%- for parent_task in parent_tasks -%}{{parent_task.nice_name}}/{%- endfor -%}',
            filename='{{task.nice_name}}_{{version.take_name}}_v{{"%03d"|format(version.version_number)}}{{extension}}',
        )
        self.test_project.structure.templates.append(ft)
        new_version1 = Version(**self.kwargs)
        DBSession.add(new_version1)
        DBSession.commit()

        new_version1.update_paths()
        new_version1.extension = '.ma'
        self.assertEqual(new_version1.extension, '.ma')

        self.assertEqual(
            new_version1.absolute_path,
            '/mnt/T/tp/SH001/Task1'
        )
