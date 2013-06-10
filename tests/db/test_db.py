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

import os
import shutil
import datetime
import unittest2
import tempfile
from sqlalchemy.exc import IntegrityError

from stalker.db.session import DBSession, ZopeTransactionExtension
from stalker import (db, defaults, Asset, Department, SimpleEntity, Entity,
                     ImageFormat, Link, Note, Project, Repository, Sequence,
                     Shot, Status, StatusList, Structure, Tag, Task, Type,
                     FilenameTemplate, User, Version, Permission, Group,
                     TimeLog, Ticket, Scene, WorkingHours, Studio, Vacation)
import logging
from stalker import log

logger = logging.getLogger(__name__)
logger.setLevel(log.logging_level)


class DatabaseTester(unittest2.TestCase):
    """tests the database and connection to the database
    """

    @classmethod
    def setUpClass(cls):
        """set up the test for class
        """
        DBSession.remove()
        DBSession.configure(extension=None)

    @classmethod
    def tearDownClass(cls):
        """clean up the test
        """
        DBSession.configure(extension=ZopeTransactionExtension())

    def setUp(self):
        """setup the tests
        """
        # just set the default admin creation to true
        # some tests are relying on that
        defaults.auto_create_admin = True
        defaults.admin_name = "admin"
        defaults.admin_password = "admin"

        self.TEST_DATABASE_URI = "sqlite:///:memory:"

        self._createdDB = False

    def tearDown(self):
        """tearDown the tests
        """
        DBSession.remove()

    def test_creating_a_custom_in_memory_db(self):
        """testing if a custom in-memory sqlite database will be created
        """
        # create a database in memory
        db.setup({
            "sqlalchemy.url": "sqlite:///:memory:",
            "sqlalchemy.echo": False,
        })

        # try to persist a user and get it back
        # create a new user
        kwargs = {
            "name": "Erkan Ozgur Yilmaz",
            "login": "eoyilmaz",
            "email": "eoyilmaz@gmail.com",
            #"created_by": admin,
            "password": "password",
        }

        newUser = User(**kwargs)
        DBSession.add(newUser)
        DBSession.commit()

        # now check if the newUser is there
        newUser_DB = User.query.filter_by(name=kwargs["name"]).first()

        self.assertTrue(newUser_DB is not None)

    #    def test_creating_a_custom_sqlite_db(self):
    #        """testing if a custom sqlite database will be created in the given
    #        location
    #        """
    #        self.TEST_DATABASE_FILE = tempfile.mktemp() + ".db"
    #        self.TEST_DATABASE_DIALECT = "sqlite:///"
    #        self.TEST_DATABASE_URI = self.TEST_DATABASE_DIALECT +\
    #                                 self.TEST_DATABASE_FILE
    #        
    #        # check if there is no file with the same name
    #        self.assertFalse(os.path.exists(self.TEST_DATABASE_FILE))
    #        
    #        DBSession.remove()
    #        # setup the database
    #        db.setup({
    #            "sqlalchemy.url": self.TEST_DATABASE_URI,
    #            "sqlalchemy.echo": False,
    #        })
    #        
    #        # check if the file is created
    #        self.assertTrue(os.path.exists(self.TEST_DATABASE_FILE))
    #        
    #        # create a new user
    #        kwargs = {
    #            "name": "Erkan Ozgur Yilmaz",
    #            "login": "eoyilmaz",
    #            "email": "eoyilmaz@gmail.com",
    #            "password": "password",
    #        }
    #        
    #        newUser = User(**kwargs)
    #        DBSession.add(newUser)
    #        DBSession.commit()
    #        
    #        # now reconnect and check if the newUser is there
    #        DBSession.remove()
    #        
    #        db.setup({
    #            "sqlalchemy.url": self.TEST_DATABASE_URI,
    #            "sqlalchemy.echo": False
    #        })
    #        
    #        newUser_DB = User.query.filter_by(name=kwargs["name"]).first()
    #        
    #        self.assertTrue(newUser_DB is not None)
    #        
    #        # delete the temp file
    #        os.remove(self.TEST_DATABASE_FILE)
    #        DBSession.remove()

    def test_default_admin_creation(self):
        """testing if a default admin is created
        """
        # set default admin creation to True
        defaults.auto_create_admin = True

        db.setup()

        # check if there is an admin
        admin_DB = User.query.filter(User.name == defaults.admin_name).first()

        self.assertEqual(admin_DB.name, defaults.admin_name)

    def test_default_admin_for_already_created_databases(self):
        """testing if no extra admin is going to be created for already setup
        databases
        """
        # set default admin creation to True
        defaults.auto_create_admin = True

        db.setup({
            "sqlalchemy.url": self.TEST_DATABASE_URI
        })

        # try to call the db.setup for a second time and see if there are more
        # than one admin

        db.setup({
            "sqlalchemy.url": self.TEST_DATABASE_URI
        })

        self._createdDB = True

        # and get how many admin is created, (it is imipossible to create
        # second one because the tables.simpleEntity.c.nam.unique=True

        admins = User.query.filter_by(name=defaults.admin_name).all()

        self.assertTrue(len(admins) == 1)

    #    def test_auth_authenticate_LogginError_raised(self):
    #        """testing if stalker.errors.LoginError will be raised when
    #        authentication information is wrong
    #        """
    #        
    #        db.setup()
    #        
    #        test_datas = [
    #            ("", ""),
    #            ("a user name", ""),
    #            ("", "just a pass"),
    #            ("no correct user", "wrong pass")
    #        ]
    #
    #        for user_name, password in test_datas:
    #            self.assertRaises(
    #                LoginError,
    #                auth.authenticate,
    #                user_name,
    #                password
    #            )

    def test_no_default_admin_creation(self):
        """testing if there is no user if stalker.config.Conf.auto_create_admin
        is False
        """
        # turn down auto admin creation
        defaults.auto_create_admin = False

        # setup the db
        db.setup()

        # check if there is a use with name admin
        self.assertTrue(
            User.query.filter_by(name=defaults.admin_name).first()
            is None
        )

        # check if there is a admins department
        self.assertTrue(
            Department.query
            .filter_by(name=defaults.admin_department_name)
            .first() is None
        )

    def test_non_unique_names_on_different_entity_type(self):
        """testing if there can be non-unique names for different entity types
        """
        db.setup()

        # try to create a user and an entity with same name
        # expect Nothing
        kwargs = {
            "name": "user1",
            #"created_by": admin
        }

        entity1 = Entity(**kwargs)
        DBSession.add(entity1)
        DBSession.commit()

        # lets create the second user
        kwargs.update({
            "name": "User1 Name",
            "login": "user1",
            "email": "user1@gmail.com",
            "password": "user1",
        })

        user1 = User(**kwargs)
        DBSession.add(user1)

        # expect nothing, this should work without any error
        DBSession.commit()

    #    def test_entity_types_table_is_created_properly(self):
    #        """testing if the entity_types table is created properly
    #        """
    #        
    #        db.setup()
    #        
    #        # check if db.metadata.tables has a table with name entity_types
    #        self.assertTrue("entity_types", db.metadata.tables)

    def test_ticket_status_initialization(self):
        """testing if the ticket statuses are correctly created
        """
        db.setup()

        #ticket_statuses = Status.query.all()
        ticket_status_list = StatusList.query \
            .filter(StatusList.name == 'Ticket Statuses') \
            .first()

        self.assertTrue(isinstance(ticket_status_list, StatusList))

        expected_status_names = ['New', 'Reopened', 'Closed', 'Accepted',
                                 'Assigned']
        self.assertEqual(len(ticket_status_list.statuses),
                         len(expected_status_names))
        for status in ticket_status_list.statuses:
            self.assertTrue(status.name in expected_status_names)

    # def test_time_log_type_initialization(self):
    #     """testing if the TimeLog types are correctly created
    #     """
    #     db.setup()
    # 
    #     time_log_types = Type.query \
    #         .filter(Type.target_entity_type == 'TimeLog') \
    #         .all()
    # 
    #     expected_type_names = ['Normal', 'Extra']
    #     self.assertEqual(len(time_log_types), len(expected_type_names))
    #     for type_ in time_log_types:
    #         self.assertTrue(type_.name in expected_type_names)

    def test_register_creates_suitable_Permissions(self):
        """testing if stalker.db.register is able to create suitable
        Permissions
        """
        db.setup()

        # create a new dummy class
        class TestClass(object):
            pass

        db.register(TestClass)

        # now check if the TestClass entry is created in Permission table

        permissions_DB = Permission.query \
            .filter(Permission.class_name == 'TestClass') \
            .all()

        logger.debug("%s" % permissions_DB)

        actions = defaults.actions

        for action in permissions_DB:
            self.assertTrue(action.action in actions)

    def test_register_raise_TypeError_for_wrong_class_name_argument(self):
        """testing if a TypeError will be raised if the class_name argument is
        not an instance of type or str or unicode
        """
        db.setup()
        self.assertRaises(TypeError, db.register, 23425)

    def test_setup_calls_the_callback_function(self):
        """testing if setup will call the given callback function
        """

        def test_func():
            raise RuntimeError

        self.assertRaises(RuntimeError, db.setup, **{"callback": test_func})

    def test_permissions_created_for_all_the_classes(self):
        """testing if Permission instances are created for classes in the SOM
        """
        DBSession.remove()
        DBSession.configure(extension=None)
        db.setup()

        class_names = [
            'Asset', 'Group', 'Permission', 'User', 'Department',
            'SimpleEntity', 'Entity', 'ImageFormat', 'Link', 'Message', 'Note',
            'Project', 'Repository', 'Scene', 'Sequence', 'Shot', 'Status',
            'StatusList', 'Structure', 'Studio', 'Tag', 'TimeLog', 'Task',
            'FilenameTemplate', 'Ticket', 'TicketLog', 'Type', 'Version',
        ]

        permission_DB = Permission.query.all()

        self.assertEqual(
            len(permission_DB),
            len(class_names) * len(defaults.actions) * 2
        )

        from pyramid.security import Allow, Deny

        for permission in permission_DB:
            self.assertTrue(permission.access in [Allow, Deny])
            self.assertTrue(permission.action in defaults.actions)
            self.assertTrue(permission.class_name in class_names)
            logger.debug('permission.access: %s' % permission.access)
            logger.debug('permission.action: %s' % permission.action)
            logger.debug('permission.class_name: %s' % permission.class_name)

    def test_permissions_not_created_over_and_over_again(self):
        """testing if the Permissions are created only once and trying to call
        __init_db__ will not raise any error
        """
        # create the environment variable and point it to a temp directory
        temp_db_path = tempfile.mkdtemp()
        temp_db_filename = 'stalker.db'
        temp_db_full_path = os.path.join(temp_db_path, temp_db_filename)

        temp_db_url = 'sqlite:///' + temp_db_full_path

        DBSession.remove()
        db.setup(settings={'sqlalchemy.url': temp_db_url})

        # this should not give any error
        DBSession.remove()
        db.setup(settings={'sqlalchemy.url': temp_db_url})

        # and we still have correct amount of Permissions
        permissions = Permission.query.all()
        self.assertEqual(len(permissions), 280)

        # clean the test
        shutil.rmtree(temp_db_path)


class DatabaseModelsTester(unittest2.TestCase):
    """tests the database model
    
    NOTE TO OTHER DEVELOPERS:
    
    Most of the tests in this TestCase uses parts of the system which are
    tested but probably not tested while running the individual tests.
    
    Incomplete isolation is against to the logic behind unittesting, every test
    should only cover a unit of the code, and a complete isolation should be
    created. But this can not be done in persistence tests (AFAIK), it needs to
    be done in this way for now. Mocks can not be used because every created
    object goes to the database, so they need to be real objects.
    """

    @classmethod
    def setUpClass(cls):
        """setup the test
        """
        # use a normal session instead of a managed one
        DBSession.remove()
        DBSession.configure(extension=None)

    @classmethod
    def tearDownClass(cls):
        """clean up the test
        """
        # delete the default test database file
        #os.remove(cls.TEST_DATABASE_FILE)
        DBSession.configure(extension=ZopeTransactionExtension())

    def setUp(self):
        """setup the test
        """
        # create a test database, possibly an in memory datase
        self.TEST_DATABASE_FILE = ":memory:"
        self.TEST_DATABASE_URI = "sqlite:///" + self.TEST_DATABASE_FILE

        db.setup()

    def tearDown(self):
        """tearing down the test
        """
        DBSession.remove()

    def test_persistence_of_Asset(self):
        """testing the persistence of Asset
        """
        asset_type = Type(
            name='A new asset type A',
            code='anata',
            target_entity_type=Asset
        )

        status1 = Status(name='On Hold A', code='OHA')
        status2 = Status(name='Completed A', code='CMPLTA')
        status3 = Status(name='Work In Progress A', code='WIPA')

        test_repository_type = Type(
            name='Test Repository Type A',
            code='trta',
            target_entity_type=Repository,
        )

        test_repository = Repository(
            name='Test Repository A',
            type=test_repository_type
        )

        project_statusList = StatusList(
            name='Project Status List A',
            statuses=[status1, status2, status3],
            target_entity_type='Project',
        )

        commercial_type = Type(
            name='Commercial A',
            code='comm',
            target_entity_type=Project
        )

        test_project = Project(
            name='Test Project For Asset Creation',
            code='TPFAC',
            status_list=project_statusList,
            type=commercial_type,
            repository=test_repository,
        )

        DBSession.add(test_project)
        DBSession.commit()

        task_status_list = StatusList(
            name='Task Status List',
            statuses=[status1, status2, status3],
            target_entity_type=Task,
        )

        asset_statusList = StatusList(
            name='Asset Status List',
            statuses=[status1, status2, status3],
            target_entity_type=Asset
        )

        kwargs = {
            'name': 'Test Asset',
            'code': 'test_asset',
            'description': 'This is a test Asset object',
            'type': asset_type,
            'project': test_project,
            'status_list': asset_statusList,
        }

        test_asset = Asset(**kwargs)
        # logger.debug('test_asset.project : %s' % test_asset.project)

        DBSession.add(test_asset)
        DBSession.commit()

        # logger.debug('test_asset.project (after commit): %s' % 
        #              test_asset.project)

        mock_task1 = Task(
            name='test task 1', status=0,
            status_list=task_status_list,
            parent=test_asset,
        )

        mock_task2 = Task(
            name='test task 2', status=0,
            status_list=task_status_list,
            parent=test_asset,
        )

        mock_task3 = Task(
            name='test task 3', status=0,
            status_list=task_status_list,
            parent=test_asset,
        )

        DBSession.add_all([mock_task1, mock_task2, mock_task3])
        DBSession.commit()

        code = test_asset.code
        created_by = test_asset.created_by
        date_created = test_asset.date_created
        date_updated = test_asset.date_updated
        duration = test_asset.duration
        description = test_asset.description
        end = test_asset.end
        name = test_asset.name
        nice_name = test_asset.nice_name
        notes = test_asset.notes
        project = test_asset.project
        references = test_asset.references
        status = test_asset.status
        status_list = test_asset.status_list
        start = test_asset.start
        tags = test_asset.tags
        children = test_asset.children
        type_ = test_asset.type
        updated_by = test_asset.updated_by

        del test_asset

        test_asset_DB = Asset.query.filter_by(name=kwargs['name']).one()

        assert (isinstance(test_asset_DB, Asset))

        #self.assertEqual(test_asset, test_asset_DB)
        self.assertEqual(code, test_asset_DB.code)
        self.assertEqual(created_by, test_asset_DB.created_by)
        self.assertEqual(date_created, test_asset_DB.date_created)
        self.assertEqual(date_updated, test_asset_DB.date_updated)
        self.assertEqual(description, test_asset_DB.description)
        self.assertEqual(duration, test_asset_DB.duration)
        self.assertEqual(end, test_asset_DB.end)
        self.assertEqual(name, test_asset_DB.name)
        self.assertEqual(nice_name, test_asset_DB.nice_name)
        self.assertEqual(notes, test_asset_DB.notes)
        self.assertEqual(project, test_asset_DB.project)
        self.assertEqual(references, test_asset_DB.references)
        self.assertEqual(status, test_asset_DB.status)
        self.assertEqual(status_list, test_asset_DB.status_list)
        self.assertEqual(tags, test_asset_DB.tags)
        self.assertEqual(children, test_asset_DB.children)
        self.assertEqual(type_, test_asset_DB.type)
        self.assertEqual(updated_by, test_asset_DB.updated_by)

    def test_persistence_of_TimeLog(self):
        """testing the persistence of TimeLog
        """
        logger.setLevel(log.logging_level)

        name = 'Test TimeLog'
        description = 'this is a time log'
        created_by = None
        updated_by = None
        date_created = datetime.datetime.now()
        date_updated = datetime.datetime.now()
        start = datetime.datetime(2013, 1, 10)
        end = datetime.datetime(2013, 1, 13)

        user1 = User(
            name='User1',
            login='user1',
            email='user1@users.com',
            password='pass'
        )

        user2 = User(
            name='User2',
            login='user2',
            email='user2@users.com',
            password='pass'
        )

        stat1 = Status(
            name='Work In Progress',
            code='WIP'
        )

        stat2 = Status(
            name='Completed',
            code='CMPL'
        )

        repo = Repository(
            name='Commercials Repository',
            linux_path='/mnt/shows',
            windows_path='S:/',
            osx_path='/mnt/shows'
        )

        proj_status_list = StatusList(
            name='Project Statuses',
            statuses=[stat1, stat2],
            target_entity_type='Project'
        )

        task_status_list = StatusList(
            name='Task Statuses',
            statuses=[stat1, stat2],
            target_entity_type='Task'
        )

        projtype = Type(
            name='Commercial Project',
            code='comm',
            target_entity_type='Project'
        )

        proj1 = Project(
            name='Test Project',
            code='tp',
            type=projtype,
            status_list=proj_status_list,
            repository=repo
        )

        test_task = Task(
            name='Test Task',
            start=start,
            end=end,
            resources=[user1, user2],
            project=proj1,
            status_list=task_status_list
        )

        test_time_log = TimeLog(
            task=test_task,
            resource=user1,
            start=datetime.datetime(2013, 1, 10),
            end=datetime.datetime(2013, 1, 13)
        )

    #        DBSession.add(test_time_log)
    #        DBSession.commit()
    #        
    #        del test_time_log
    #        
    #        # now retrieve it back
    #        test_time_log_DB = TimeLog.query.filter_by(name=name).first()
    #        
    #        self.assertEqual(date_created, test_time_log_DB.date_created)
    #        self.assertEqual(date_updated, test_time_log_DB.date_updated)
    #        self.assertEqual(start, test_time_log_DB.start)
    #        self.assertEqual(end, test_time_log_DB.end)
    #        self.assertEqual(user1, test_time_log_DB.user1)


    def test_persistence_of_Department(self):
        """testing the persistence of Department
        """
        logger.setLevel(log.logging_level)

        name = "TestDepartment_test_persistence_Department"
        description = "this is for testing purposes"
        created_by = None
        updated_by = None
        date_created = datetime.datetime.now()
        date_updated = datetime.datetime.now()

        test_dep = Department(
            name=name,
            description=description,
            created_by=created_by,
            updated_by=updated_by,
            date_created=date_created,
            date_updated=date_updated
        )
        DBSession.add(test_dep)
        DBSession.commit()

        # create three users, one for lead and two for members

        # user1
        user1 = User(
            name="User1 Test Persistence Department",
            login='u1tpd',
            initials='u1tpd',
            description="this is for testing purposes",
            created_by=None,
            updated_by=None,
            login_name="user1_tp_department",
            first_name="user1_first_name",
            last_name="user1_last_name",
            email="user1@department.com",
            department=test_dep,
            password="password",
        )

        # user2
        user2 = User(
            name="User2 Test Persistence Department",
            login='u2tpd',
            initials='u2tpd',
            description="this is for testing purposes",
            created_by=None,
            updated_by=None,
            login_name="user2_tp_department",
            first_name="user2_first_name",
            last_name="user2_last_name",
            email="user2@department.com",
            department=test_dep,
            password="password",
        )

        # user3
        # create three users, one for lead and two for members
        user3 = User(
            name="User3 Test Persistence Department",
            login='u2tpd',
            initials='u2tpd',
            description="this is for testing purposes",
            created_by=None,
            updated_by=None,
            login_name="user3_tp_department",
            first_name="user3_first_name",
            last_name="user3_last_name",
            email="user3@department.com",
            department=test_dep,
            password="password",
        )

        # add as the members and the lead
        test_dep.lead = user1
        test_dep.members = [user1, user2, user3]

        DBSession.add(test_dep)
        DBSession.commit()

        self.assertTrue(test_dep in DBSession)

        created_by = test_dep.created_by
        date_created = test_dep.date_created
        date_updated = test_dep.date_updated
        description = test_dep.description
        lead = test_dep.lead
        members = test_dep.members
        name = test_dep.name
        nice_name = test_dep.nice_name
        notes = test_dep.notes
        tags = test_dep.tags
        updated_by = test_dep.updated_by

        del test_dep

        # lets check the data
        # first get the department from the db
        test_dep_db = Department.query.filter_by(name=name).first()

        assert (isinstance(test_dep_db, Department))

        self.assertEqual(created_by, test_dep_db.created_by)
        self.assertEqual(date_created, test_dep_db.date_created)
        self.assertEqual(date_updated, test_dep_db.date_updated)
        self.assertEqual(description, test_dep_db.description)
        self.assertEqual(lead, test_dep_db.lead)
        self.assertEqual(members, test_dep_db.members)
        self.assertEqual(name, test_dep_db.name)
        self.assertEqual(nice_name, test_dep_db.nice_name)
        self.assertEqual(notes, test_dep_db.notes)
        self.assertEqual(tags, test_dep_db.tags)
        self.assertEqual(updated_by, test_dep_db.updated_by)

    def test_persistence_of_Entity(self):
        """testing the persistence of Entity
        """

        # create an Entity with a couple of tags
        # the Tag1
        name = "Tag1_test_creating_an_Entity"
        description = "this is for testing purposes"
        created_by = None
        updated_by = None
        date_created = date_updated = datetime.datetime.now()

        tag1 = Tag(
            name=name,
            description=description,
            created_by=created_by,
            updated_by=updated_by,
            date_created=date_created,
            date_updated=date_updated
        )

        # the Tag2
        name = "Tag2_test_creating_an_Entity"
        description = "this is for testing purposes"
        created_by = None
        updated_by = None
        date_created = date_updated = datetime.datetime.now()

        tag2 = Tag(
            name=name,
            description=description,
            created_by=created_by,
            updated_by=updated_by,
            date_created=date_created,
            date_updated=date_updated
        )

        # the note
        note1 = Note(name="test note")

        # the entity
        name = "TestEntity"
        description = "this is for testing purposes"
        created_by = None
        updated_by = None
        date_created = date_updated = datetime.datetime.now()

        test_entity = Entity(
            name=name,
            description=description,
            created_by=created_by,
            updated_by=updated_by,
            date_created=date_created,
            date_updated=date_updated,
            tags=[tag1, tag2],
            notes=[note1],
        )

        # persist it to the database
        DBSession.add(test_entity)
        DBSession.commit()

        # store attributes
        created_by = test_entity.created_by
        date_created = test_entity.date_created
        date_updated = test_entity.date_updated
        description = test_entity.description
        name = test_entity.name
        nice_name = test_entity.nice_name
        notes = test_entity.notes
        tags = test_entity.tags
        updated_by = test_entity.updated_by

        # delete the previous test_entity
        del test_entity

        # now try to retrieve it
        test_entity_DB = Entity.query.filter_by(name=name).first()

        assert (isinstance(test_entity_DB, Entity))

        #self.assertEqual(test_entity, test_entity_DB)
        self.assertEqual(created_by, test_entity_DB.created_by)
        self.assertEqual(date_created, test_entity_DB.date_created)
        self.assertEqual(date_updated, test_entity_DB.date_updated)
        self.assertEqual(description, test_entity_DB.description)
        self.assertEqual(name, test_entity_DB.name)
        self.assertEqual(nice_name, test_entity_DB.nice_name)
        self.assertEqual(notes, test_entity_DB.notes)
        self.assertEqual(tags, test_entity_DB.tags)
        self.assertEqual(updated_by, test_entity_DB.updated_by)

    def test_persistence_of_FilenameTemplate(self):
        """testing the persistence of FilenameTemplate
        """

        vers_type = Type.query.filter_by(name="Version").first()
        ref_type = Type.query.filter_by(name="Reference").first()

        # create a FilenameTemplate object for movie links
        kwargs = {
            "name": "Movie Links Template",
            "target_entity_type": Link,
            "type": ref_type,
            "description": "this is a template to be used for links to movie"
                           "files",
            "path": "REFS/{{link_type.name}}",
            "filename": "{{link.file_name}}",
            "output_path": "OUTPUT",
            "output_file_code": "{{link.file_name}}",
        }

        new_type_template = FilenameTemplate(**kwargs)
        #new_type_template2 = FilenameTemplate(**kwargs)

        # persist it
        DBSession.add(new_type_template)
        DBSession.commit()

        created_by = new_type_template.created_by
        date_created = new_type_template.date_created
        date_updated = new_type_template.date_updated
        description = new_type_template.description
        filename = new_type_template.filename
        name = new_type_template.name
        nice_name = new_type_template.nice_name
        notes = new_type_template.notes
        path = new_type_template.path
        tags = new_type_template.tags
        target_entity_type = new_type_template.target_entity_type
        updated_by = new_type_template.updated_by
        type_ = new_type_template.type

        del new_type_template

        # get it back
        new_type_template_DB = \
            FilenameTemplate.query.filter_by(name=kwargs["name"]).first()

        assert (isinstance(new_type_template_DB, FilenameTemplate))

        self.assertEqual(created_by, new_type_template_DB.created_by)
        self.assertEqual(date_created, new_type_template_DB.date_created)
        self.assertEqual(date_updated, new_type_template_DB.date_updated)
        self.assertEqual(description, new_type_template_DB.description)
        self.assertEqual(filename, new_type_template_DB.filename)
        self.assertEqual(name, new_type_template_DB.name)
        self.assertEqual(nice_name, new_type_template_DB.nice_name)
        self.assertEqual(notes, new_type_template_DB.notes)
        self.assertEqual(path, new_type_template_DB.path)
        self.assertEqual(tags, new_type_template_DB.tags)
        self.assertEqual(target_entity_type,
                         new_type_template_DB.target_entity_type)
        self.assertEqual(updated_by, new_type_template_DB.updated_by)
        self.assertEqual(type_, new_type_template_DB.type)

    def test_persistence_of_ImageFormat(self):
        """testing the persistence of ImageFormat
        """
        # create a new ImageFormat object and try to read it back
        kwargs = {
            "name": "HD",
            "description": "test image format",
            #"created_by": admin,
            #"updated_by": admin,
            "width": 1920,
            "height": 1080,
            "pixel_aspect": 1.0,
            "print_resolution": 300.0
        }

        # create the ImageFormat object
        im_format = ImageFormat(**kwargs)

        # persist it
        DBSession.add(im_format)
        DBSession.commit()

        # store attributes
        created_by = im_format.created_by
        date_created = im_format.date_created
        date_updated = im_format.date_updated
        description = im_format.description
        device_aspect = im_format.device_aspect
        height = im_format.height
        name = im_format.name
        nice_name = im_format.nice_name
        notes = im_format.notes
        pixel_aspect = im_format.pixel_aspect
        print_resolution = im_format.print_resolution
        tags = im_format.tags
        updated_by = im_format.updated_by
        width = im_format.width

        # delete the previous im_format
        del im_format

        # get it back
        im_format_DB = ImageFormat.query.filter_by(name=kwargs["name"]).first()

        assert (isinstance(im_format_DB, ImageFormat))

        # just test the repository part of the attributes
        #self.assertEqual(im_format, im_format_DB)
        self.assertEqual(created_by, im_format_DB.created_by)
        self.assertEqual(date_created, im_format_DB.date_created)
        self.assertEqual(date_updated, im_format_DB.date_updated)
        self.assertEqual(description, im_format_DB.description)
        self.assertEqual(device_aspect, im_format_DB.device_aspect)
        self.assertEqual(height, im_format_DB.height)
        self.assertEqual(name, im_format_DB.name)
        self.assertEqual(nice_name, im_format_DB.nice_name)
        self.assertEqual(notes, im_format_DB.notes)
        self.assertEqual(pixel_aspect, im_format_DB.pixel_aspect)
        self.assertEqual(print_resolution, im_format_DB.print_resolution)
        self.assertEqual(tags, im_format_DB.tags)
        self.assertEqual(updated_by, im_format_DB.updated_by)
        self.assertEqual(width, im_format_DB.width)

    def test_persistence_of_Link(self):
        """testing the persistence of Link
        """
        # create a link Type
        sound_link_type = Type(
            name='Sound',
            code='sound',
            target_entity_type=Link
        )

        # create a Link
        kwargs = {
            'name': 'My Sound',
            'full_path': 'M:/PROJECTS/my_movie_sound.wav',
            'type': sound_link_type
        }

        new_link = Link(**kwargs)

        # persist it
        DBSession.add_all([sound_link_type, new_link])
        DBSession.commit()

        # store attributes
        created_by = new_link.created_by
        date_created = new_link.date_created
        date_updated = new_link.date_updated
        description = new_link.description
        name = new_link.name
        nice_name = new_link.nice_name
        notes = new_link.notes
        full_path = new_link.full_path
        tags = new_link.tags
        type_ = new_link.type
        updated_by = new_link.updated_by

        # delete the link
        del new_link

        # retrieve it back
        new_link_DB = Link.query.filter_by(name=kwargs["name"]).first()

        assert (isinstance(new_link_DB, Link))

        #self.assertEqual(new_link, new_link_DB)
        self.assertEqual(created_by, new_link_DB.created_by)
        self.assertEqual(date_created, new_link_DB.date_created)
        self.assertEqual(date_updated, new_link_DB.date_updated)
        self.assertEqual(description, new_link_DB.description)
        self.assertEqual(name, new_link_DB.name)
        self.assertEqual(nice_name, new_link_DB.nice_name)
        self.assertEqual(notes, new_link_DB.notes)
        self.assertEqual(full_path, new_link_DB.full_path)
        self.assertEqual(tags, new_link_DB.tags)
        self.assertEqual(type_, new_link_DB.type)
        self.assertEqual(updated_by, new_link_DB.updated_by)

    def test_persistence_of_Note(self):
        """testing the persistence of Note
        """

        # create a Note and attach it to an entity

        # create a Note object
        note_kwargs = {
            "name": "Note1",
            "description": "This Note is created for the purpose of testing \
            the Note object",
            "content": "Please be carefull about this asset, I will fix the \
            rig later on",
        }

        test_note = Note(**note_kwargs)

        # create an entity
        entity_kwargs = {
            "name": "Entity with Note",
            "description": "This Entity is created for testing purposes",
            "notes": [test_note],
        }

        test_entity = Entity(**entity_kwargs)

        DBSession.add_all([test_entity, test_note])
        DBSession.commit()

        # store the attributes
        content = test_note.content
        created_by = test_note.created_by
        date_created = test_note.date_created
        date_updated = test_note.date_updated
        description = test_note.description
        name = test_note.name
        nice_name = test_note.nice_name
        updated_by = test_note.updated_by

        # delete the note
        del test_note

        # try to get the note directly
        test_note_DB = \
            Note.query.filter(Note.name == note_kwargs["name"]).first()

        assert (isinstance(test_note_DB, Note))

        # try to get the note from the entity
        test_entity_DB = \
            Entity.query.filter(Entity.name == entity_kwargs["name"]).first()

        self.assertEqual(content, test_note_DB.content)
        self.assertEqual(created_by, test_note_DB.created_by)
        self.assertEqual(date_created, test_note_DB.date_created)
        self.assertEqual(date_updated, test_note_DB.date_updated)
        self.assertEqual(description, test_note_DB.description)
        self.assertEqual(name, test_note_DB.name)
        self.assertEqual(nice_name, test_note_DB.nice_name)
        self.assertEqual(updated_by, test_note_DB.updated_by)

    def test_persistence_of_Group(self):
        """testing the persistence of Group
        """

        group1 = Group(
            name='Test Group'
        )

        user1 = User(
            name='User1',
            login='user1',
            email='user1@test.com',
            password='12'
        )
        user2 = User(
            name='User2',
            login='user2',
            email='user2@test.com',
            password='34'
        )

        group1.users = [user1, user2]

        DBSession.add(group1)
        DBSession.commit()

        name = group1.name
        users = group1.users

        del group1
        group_DB = Group.query.filter_by(name=name).first()

        self.assertEqual(name, group_DB.name)
        self.assertEqual(users, group_DB.users)

    def test_persistence_of_Project(self):
        """testing the persistence of Project
        """
        # create mock objects
        start = datetime.date.today() + datetime.timedelta(10)
        end = start + datetime.timedelta(days=20)

        lead = User(
            name="lead",
            login="lead",
            email="lead@lead.com",
            password="password"
        )

        user1 = User(
            name="user1",
            login="user1",
            email="user1@user1.com",
            password="password"
        )

        user2 = User(
            name="user2",
            login="user2",
            email="user1@user2.com",
            password="password"
        )

        user3 = User(
            name="user3",
            login="user3",
            email="user3@user3.com",
            password="password"
        )

        image_format = ImageFormat(
            name="HD",
            width=1920,
            height=1080
        )

        project_type = Type(
            name='Commercial Project',
            code='commproj',
            target_entity_type=Project
        )

        structure_type = Type(
            name='Commercial Structure',
            code='commstr',
            target_entity_type=Project
        )

        project_structure = Structure(
            name="Commercial Structure",
            custom_templates="{{project.code}}\n"
                             "{{project.code}}/ASSETS\n"
                             "{{project.code}}/SEQUENCES\n",
            type=structure_type,
        )

        repo = Repository(
            name="Commercials Repository",
            linux_path="/mnt/M/Projects",
            windows_path="M:/Projects",
            osx_path="/mnt/M/Projects"
        )

        status1 = Status(
            name="On Hold",
            code="OH"
        )

        status2 = Status(
            name="Complete",
            code="CMPLT"
        )

        project_status_list = StatusList(
            name="A Status List for testing Project",
            statuses=[status1, status2],
            target_entity_type=Project
        )

        DBSession.add(project_status_list)
        DBSession.commit()

        # create data for mixins
        # Reference Mixin
        link_type = Type(
            name='Image',
            code='image',
            target_entity_type='Link'
        )

        ref1 = Link(
            name="Ref1",
            full_path="/mnt/M/JOBs/TEST_PROJECT",
            filename="1.jpg",
            type=link_type
        )

        ref2 = Link(
            name="Ref2",
            full_path="/mnt/M/JOBs/TEST_PROJECT",
            filename="1.jpg",
            type=link_type
        )

        # TaskMixin
        task_status_list = StatusList(
            name="Task Statuses",
            statuses=[status1, status2],
            target_entity_type=Task
        )

        DBSession.add(task_status_list)
        DBSession.add_all([ref1, ref2])
        DBSession.commit()

        working_hours = WorkingHours(
            working_hours={
                'mon': [[570, 720], [780, 1170]],
                'tue': [[570, 720], [780, 1170]],
                'wed': [[570, 720], [780, 1170]],
                'thu': [[570, 720], [780, 1170]],
                'fri': [[570, 720], [780, 1170]],
                'sat': [[570, 720], [780, 1170]],
                'sun': [],
            }
        )

        # create a project object
        kwargs = {
            'name': 'Test Project',
            'code': 'TP',
            'description': 'This is a project object for testing purposes',
            'lead': lead,
            'image_format': image_format,
            'fps': 25,
            'type': project_type,
            'structure': project_structure,
            'repository': repo,
            'is_stereoscopic': False,
            'display_width': 1.0,
            'start': start,
            'end': end,
            'status_list': project_status_list,
            'status': 0,
            'references': [ref1, ref2],
            'working_hours': working_hours
        }

        new_project = Project(**kwargs)

        # persist it in the database
        DBSession.add(new_project)
        DBSession.commit()

        task1 = Task(
            name="task1",
            status_list=task_status_list,
            status=0,
            project=new_project,
        )

        task2 = Task(
            name="task2",
            status_list=task_status_list,
            status=0,
            project=new_project,
        )

        new_project._computed_start = datetime.datetime.now()
        new_project._computed_end = datetime.datetime.now() \
                                    + datetime.timedelta(10)

        DBSession.add_all([task1, task2])
        DBSession.commit()

        # store the attributes
        assets = new_project.assets
        code = new_project.code
        created_by = new_project.created_by
        date_created = new_project.date_created
        date_updated = new_project.date_updated
        description = new_project.description
        end = new_project.end
        duration = new_project.duration
        fps = new_project.fps
        image_format = new_project.image_format
        is_stereoscopic = new_project.is_stereoscopic
        lead = new_project.lead
        name = new_project.name
        nice_name = new_project.nice_name
        notes = new_project.notes
        references = new_project.references
        repository = new_project.repository
        sequences = new_project.sequences
        start = new_project.start
        status = new_project.status
        status_list = new_project.status_list
        structure = new_project.structure
        tags = new_project.tags
        tasks = new_project.tasks
        type = new_project.type
        updated_by = new_project.updated_by
        users = new_project.users
        computed_start = new_project.computed_start
        computed_end = new_project.computed_end
        timing_resolution = new_project.timing_resolution

        # delete the project
        del new_project

        # now get it
        new_project_DB = DBSession.query(Project). \
            filter_by(name=kwargs["name"]).first()

        assert (isinstance(new_project_DB, Project))

        #self.assertEqual(new_project, new_project_DB)
        self.assertEqual(assets, new_project_DB.assets)
        self.assertEqual(code, new_project_DB.code)
        self.assertEqual(computed_start, new_project_DB.computed_start)
        self.assertEqual(computed_end, new_project_DB.computed_end)
        self.assertEqual(created_by, new_project_DB.created_by)
        self.assertEqual(date_created, new_project_DB.date_created)
        self.assertEqual(date_updated, new_project_DB.date_updated)
        self.assertEqual(description, new_project_DB.description)
        #self.assertEqual(display_width, new_project_DB.display_width)
        self.assertEqual(end, new_project_DB.end)
        self.assertEqual(duration, new_project_DB.duration)
        self.assertEqual(fps, new_project_DB.fps)
        self.assertEqual(image_format, new_project_DB.image_format)
        self.assertEqual(is_stereoscopic, new_project_DB.is_stereoscopic)
        self.assertEqual(lead, new_project_DB.lead)
        self.assertEqual(name, new_project_DB.name)
        self.assertEqual(nice_name, new_project_DB.nice_name)
        self.assertEqual(notes, new_project_DB.notes)
        self.assertEqual(references, new_project_DB.references)
        self.assertEqual(repository, new_project_DB.repository)
        self.assertEqual(sequences, new_project_DB.sequences)
        self.assertEqual(start, new_project_DB.start)
        self.assertEqual(status, new_project_DB.status)
        self.assertEqual(status_list, new_project_DB.status_list)
        self.assertEqual(structure, new_project_DB.structure)
        self.assertEqual(tags, new_project_DB.tags)
        self.assertEqual(tasks, new_project_DB.tasks)
        self.assertEqual(timing_resolution, new_project_DB.timing_resolution)
        self.assertEqual(type, new_project_DB.type)
        self.assertEqual(updated_by, new_project_DB.updated_by)
        self.assertEqual(users, new_project_DB.users)

    def test_persistence_of_Repository(self):
        """testing the persistence of Repository
        """
        # create a new Repository object and try to read it back
        kwargs = {
            "name": "Movie-Repo",
            "description": "test repository",
            #"created_by": admin,
            #"updated_by": admin,
            "linux_path": "/mnt/M",
            "osx_path": "/mnt/M",
            "windows_path": "M:/"
        }

        # create the repository object
        repo = Repository(**kwargs)

        # save it to database
        DBSession.add(repo)
        DBSession.commit()

        # store attributes
        created_by = repo.created_by
        date_created = repo.date_created
        date_updated = repo.date_updated
        description = repo.description
        linux_path = repo.linux_path
        name = repo.name
        nice_name = repo.nice_name
        notes = repo.notes
        osx_path = repo.osx_path
        path = repo.path
        tags = repo.tags
        updated_by = repo.updated_by
        windows_path = repo.windows_path

        # delete the repo
        del repo

        # get it back
        repo_db = DBSession.query(Repository) \
            .filter_by(name=kwargs["name"]) \
            .first()

        assert (isinstance(repo_db, Repository))

        self.assertEqual(created_by, repo_db.created_by)
        self.assertEqual(date_created, repo_db.date_created)
        self.assertEqual(date_updated, repo_db.date_updated)
        self.assertEqual(description, repo_db.description)
        self.assertEqual(linux_path, repo_db.linux_path)
        self.assertEqual(name, repo_db.name)
        self.assertEqual(nice_name, repo_db.nice_name)
        self.assertEqual(notes, repo_db.notes)
        self.assertEqual(osx_path, repo_db.osx_path)
        self.assertEqual(path, repo_db.path)
        self.assertEqual(tags, repo_db.tags)
        self.assertEqual(updated_by, repo_db.updated_by)
        self.assertEqual(windows_path, repo_db.windows_path)

    def test_persistence_of_Scene(self):
        """testing the persistence of Scene
        """
        status1 = Status(name="On Hold", code="OH")
        status2 = Status(name="Work In Progress", code="WIP")
        status3 = Status(name="Finished", code="FIN")

        project_status_list = StatusList(
            name="Project Statuses",
            statuses=[status1, status2, status3],
            target_entity_type=Project
        )

        shot_status_list = StatusList(
            name="Shot Statuses",
            statuses=[status1, status2, status3],
            target_entity_type=Shot
        )

        repo1 = Repository(
            name="Commercial Repository"
        )

        commercial_project_type = Type(
            name='Commercial Project',
            code='commproj',
            target_entity_type=Project
        )

        test_project1 = Project(
            name='Test Project',
            code='TP',
            status_list=project_status_list,
            type=commercial_project_type,
            repository=repo1,
        )

        kwargs = {
            'name': 'Test Scene',
            'code': 'TSce',
            'description': 'this is a test scene',
            'project': test_project1,
        }

        test_scene = Scene(**kwargs)

        # now add the shots
        shot1 = Shot(
            code='SH001',
            project=test_project1,
            scenes=[test_scene],
            status_list=shot_status_list
        )
        shot2 = Shot(
            code='SH002',
            project=test_project1,
            scenes=[test_scene],
            status_list=shot_status_list
        )
        shot3 = Shot(
            code='SH003',
            project=test_project1,
            scenes=[test_scene],
            status_list=shot_status_list
        )

        DBSession.add(test_scene)
        DBSession.commit()

        # store the attributes
        code = test_scene.code
        created_by = test_scene.created_by
        date_created = test_scene.date_created
        date_updated = test_scene.date_updated
        description = test_scene.description
        name = test_scene.name
        nice_name = test_scene.nice_name
        notes = test_scene.notes
        project = test_scene.project
        shots = test_scene.shots
        tags = test_scene.tags
        updated_by = test_scene.updated_by

        # delete the test_sequence
        del test_scene

        test_scene_DB = Scene.query.filter_by(name=kwargs['name']).first()

        #self.assertEqual(test_sequence, test_sequence_DB)
        self.assertEqual(code, test_scene_DB.code)
        self.assertEqual(created_by, test_scene_DB.created_by)
        self.assertEqual(date_created, test_scene_DB.date_created)
        self.assertEqual(date_updated, test_scene_DB.date_updated)
        self.assertEqual(description, test_scene_DB.description)
        self.assertEqual(name, test_scene_DB.name)
        self.assertEqual(nice_name, test_scene_DB.nice_name)
        self.assertEqual(notes, test_scene_DB.notes)
        self.assertEqual(project, test_scene_DB.project)
        self.assertEqual(shots, test_scene_DB.shots)
        self.assertEqual(tags, test_scene_DB.tags)
        self.assertEqual(updated_by, test_scene_DB.updated_by)

    def test_persistence_of_Sequence(self):
        """testing the persistence of Sequence
        """

        status1 = Status(name="On Hold", code="OH")
        status2 = Status(name="Work In Progress", code="WIP")
        status3 = Status(name="Finished", code="FIN")

        project_status_list = StatusList(
            name="Project Statuses",
            statuses=[status1, status2, status3],
            target_entity_type=Project
        )

        sequence_status_list = StatusList(
            name="Sequence Statuses",
            statuses=[status1, status2, status3],
            target_entity_type=Sequence
        )

        shot_status_list = StatusList(
            name="Shot Statuses",
            statuses=[status1, status2, status3],
            target_entity_type=Shot
        )

        repo1 = Repository(
            name="Commercial Repository"
        )

        commercial_project_type = Type(
            name='Commercial Project',
            code='commproj',
            target_entity_type=Project
        )

        test_project1 = Project(
            name='Test Project',
            code='TP',
            status_list=project_status_list,
            type=commercial_project_type,
            repository=repo1,
        )

        lead = User(
            name="lead",
            login="lead",
            email="lead@lead.com",
            password="password"
        )

        kwargs = {
            'name': 'Test Sequence',
            'code': 'TS',
            'description': 'this is a test sequence',
            'project': test_project1,
            'lead': lead,
            'status_list': sequence_status_list,
            'schedule_model': 'effort',
            'schedule_timing': 50,
            'schedule_unit': 'd'
        }

        test_sequence = Sequence(**kwargs)

        # now add the shots
        shot1 = Shot(
            code='SH001',
            project=test_project1,
            sequences=[test_sequence],
            status_list=shot_status_list
        )
        shot2 = Shot(
            code='SH002',
            project=test_project1,
            sequences=[test_sequence],
            status_list=shot_status_list
        )
        shot3 = Shot(
            code='SH003',
            project=test_project1,
            sequence=test_sequence,
            status_list=shot_status_list
        )

        DBSession.add(test_sequence)
        DBSession.commit()

        # store the attributes
        code = test_sequence.code
        created_by = test_sequence.created_by
        date_created = test_sequence.date_created
        date_updated = test_sequence.date_updated
        description = test_sequence.description
        end = test_sequence.end
        lead = test_sequence.lead
        name = test_sequence.name
        nice_name = test_sequence.nice_name
        notes = test_sequence.notes
        project = test_sequence.project
        references = test_sequence.references
        shots = test_sequence.shots
        start = test_sequence.start
        status = test_sequence.status
        status_list = test_sequence.status_list
        tags = test_sequence.tags
        children = test_sequence.children
        tasks = test_sequence.tasks
        updated_by = test_sequence.updated_by
        schedule_model = test_sequence.schedule_model
        schedule_timing = test_sequence.schedule_timing
        schedule_unit = test_sequence.schedule_unit

        # delete the test_sequence
        del test_sequence

        test_sequence_DB = Sequence.query \
            .filter_by(name=kwargs['name']).first()

        #self.assertEqual(test_sequence, test_sequence_DB)
        self.assertEqual(code, test_sequence_DB.code)
        self.assertEqual(created_by, test_sequence_DB.created_by)
        self.assertEqual(date_created, test_sequence_DB.date_created)
        self.assertEqual(date_updated, test_sequence_DB.date_updated)
        self.assertEqual(description, test_sequence_DB.description)
        self.assertEqual(end, test_sequence_DB.end)
        self.assertEqual(lead, test_sequence_DB.lead)
        self.assertEqual(name, test_sequence_DB.name)
        self.assertEqual(nice_name, test_sequence_DB.nice_name)
        self.assertEqual(notes, test_sequence_DB.notes)
        self.assertEqual(project, test_sequence_DB.project)
        self.assertEqual(references, test_sequence_DB.references)
        self.assertEqual(shots, test_sequence_DB.shots)
        self.assertEqual(start, test_sequence_DB.start)
        self.assertEqual(status, test_sequence_DB.status)
        self.assertEqual(status_list, test_sequence_DB.status_list)
        self.assertEqual(tags, test_sequence_DB.tags)
        self.assertEqual(children, test_sequence_DB.children)
        self.assertEqual(tasks, test_sequence_DB.tasks)
        self.assertEqual(updated_by, test_sequence_DB.updated_by)
        self.assertEqual(schedule_model, test_sequence_DB.schedule_model)
        self.assertEqual(schedule_timing,
                         test_sequence_DB.schedule_timing)
        self.assertEqual(schedule_unit,
                         test_sequence_DB.schedule_unit)

    def test_persistence_of_Shot(self):
        """testing the persistence of Shot
        """

        status1 = Status(name="On Hold", code="OH")
        status2 = Status(name="Work In Progress", code="WIP")
        status3 = Status(name="Finished", code="FIN")

        project_status_list = StatusList(
            name="Project Statuses",
            statuses=[status1, status2, status3],
            target_entity_type=Project
        )

        sequence_status_list = StatusList(
            name="Sequence Statuses",
            statuses=[status1, status2, status3],
            target_entity_type=Sequence
        )

        shot_status_list = StatusList(
            name="Shot Statuses",
            statuses=[status1, status2, status3],
            target_entity_type=Shot
        )

        commercial_project_type = Type(
            name='Commercial Project',
            code='commproj',
            target_entity_type=Project,
        )

        repo1 = Repository(
            name="Commercial Repository"
        )

        test_project1 = Project(
            name='Test project',
            code='tp',
            status_list=project_status_list,
            type=commercial_project_type,
            repository=repo1,
        )

        lead = User(
            name="lead",
            login="lead",
            email="lead@lead.com",
            password="password"
        )

        kwargs = {
            'name': "Test Sequence 1",
            'code': 'tseq1',
            'description': 'this is a test sequence',
            'project': test_project1,
            'lead': lead,
            'status_list': sequence_status_list,
        }

        test_seq1 = Sequence(**kwargs)

        kwargs['name'] = 'Test Sequence 2'
        kwargs['code'] = 'tseq2'
        test_seq2 = Sequence(**kwargs)

        test_sce1 = Scene(
            name='Test Scene 1',
            code='tsce1',
            project=test_project1
        )

        test_sce2 = Scene(
            name='Test Scene 2',
            code='tsce2',
            project=test_project1
        )

        # now add the shots
        shot_kwargs = {
            'code': 'SH001',
            'project': test_project1,
            'sequences': [test_seq1, test_seq2],
            'scenes': [test_sce1, test_sce2],
            'status': 0,
            'status_list': shot_status_list
        }

        test_shot = Shot(**shot_kwargs)

        DBSession.add(test_shot)
        DBSession.add(test_seq1)
        DBSession.commit()

        # store the attributes
        code = test_shot.code
        children = test_shot.children
        cut_duration = test_shot.cut_duration
        cut_in = test_shot.cut_in
        cut_out = test_shot.cut_out
        date_created = test_shot.date_created
        date_updated = test_shot.date_updated
        description = test_shot.description
        name = test_shot.name
        nice_name = test_shot.nice_name
        notes = test_shot.notes
        references = test_shot.references
        sequences = test_shot.sequences
        scenes = test_shot.scenes
        status = test_shot.status
        status_list = test_shot.status_list
        tags = test_shot.tags
        tasks = test_shot.tasks
        updated_by = test_shot.updated_by

        # delete the shot
        del test_shot

        test_shot_DB = Shot.query.filter_by(code=shot_kwargs["code"]).first()

        #self.assertEqual(test_shot, test_shot_DB)
        self.assertEqual(code, test_shot_DB.code)
        self.assertEqual(children, test_shot_DB.children)
        self.assertEqual(cut_duration, test_shot_DB.cut_duration)
        self.assertEqual(cut_in, test_shot_DB.cut_in)
        self.assertEqual(cut_out, test_shot_DB.cut_out)
        self.assertEqual(date_created, test_shot_DB.date_created)
        self.assertEqual(date_updated, test_shot_DB.date_updated)
        self.assertEqual(description, test_shot_DB.description)
        self.assertEqual(name, test_shot_DB.name)
        self.assertEqual(nice_name, test_shot_DB.nice_name)
        self.assertEqual(notes, test_shot_DB.notes)
        self.assertEqual(references, test_shot_DB.references)
        self.assertEqual(scenes, test_shot_DB.scenes)
        self.assertEqual(sequences, test_shot_DB.sequences)
        self.assertEqual(status, test_shot_DB.status)
        self.assertEqual(status_list, test_shot_DB.status_list)
        self.assertEqual(tags, test_shot_DB.tags)
        self.assertEqual(tasks, test_shot_DB.tasks)
        self.assertEqual(updated_by, test_shot_DB.updated_by)

    def test_persistence_of_SimpleEntity(self):
        """testing the persistence of SimpleEntity
        """

        kwargs = {
            "name": "SimpleEntity_test_creating_of_a_SimpleEntity",
            "description": "this is for testing purposes",
        }

        test_simple_entity = SimpleEntity(**kwargs)

        # persist it to the database
        DBSession.add(test_simple_entity)
        DBSession.commit()

        created_by = test_simple_entity.created_by
        date_created = test_simple_entity.date_created
        date_updated = test_simple_entity.date_updated
        description = test_simple_entity.description
        name = test_simple_entity.name
        nice_name = test_simple_entity.nice_name
        updated_by = test_simple_entity.updated_by
        __stalker_version__ = test_simple_entity.__stalker_version__

        del test_simple_entity

        # now try to retrieve it
        test_simple_entity_DB = DBSession.query(SimpleEntity) \
            .filter(SimpleEntity.name == kwargs["name"]).first()

        assert (isinstance(test_simple_entity_DB, SimpleEntity))

        #self.assertEqual(test_simple_entity, test_simple_entity_DB)
        self.assertEqual(created_by, test_simple_entity_DB.created_by)
        self.assertEqual(date_created, test_simple_entity_DB.date_created)
        self.assertEqual(date_updated, test_simple_entity_DB.date_updated)
        self.assertEqual(description, test_simple_entity_DB.description)
        self.assertEqual(name, test_simple_entity_DB.name)
        self.assertEqual(nice_name, test_simple_entity_DB.nice_name)
        self.assertEqual(updated_by, test_simple_entity_DB.updated_by)
        self.assertEqual(__stalker_version__,
                         test_simple_entity_DB.__stalker_version__)

    def test_persistence_of_Status(self):
        """testing the persistence of Status
        """

        # the status

        kwargs = {
            "name": "TestStatus_test_creating_Status",
            "description": "this is for testing purposes",
            "code": "TSTST",
            'bg_color': 15,
            'fg_color': 105
        }

        test_status = Status(**kwargs)

        # persist it to the database
        DBSession.add(test_status)
        DBSession.commit()

        # store the attributes
        code = test_status.code
        created_by = test_status.created_by
        date_created = test_status.date_created
        date_updated = test_status.date_updated
        description = test_status.description
        name = test_status.name
        nice_name = test_status.nice_name
        notes = test_status.notes
        tags = test_status.tags
        updated_by = test_status.updated_by
        bg_color = test_status.bg_color
        fg_color = test_status.fg_color

        # delete the test_status
        del test_status

        # now try to retrieve it
        test_status_DB = DBSession.query(Status) \
            .filter(Status.name == kwargs["name"]).first()

        assert (isinstance(test_status_DB, Status))

        # just test the satuts part of the object
        #self.assertEqual(test_status, test_status_DB)
        self.assertEqual(code, test_status_DB.code)
        self.assertEqual(created_by, test_status_DB.created_by)
        self.assertEqual(date_created, test_status_DB.date_created)
        self.assertEqual(date_updated, test_status_DB.date_updated)
        self.assertEqual(description, test_status_DB.description)
        self.assertEqual(name, test_status_DB.name)
        self.assertEqual(nice_name, test_status_DB.nice_name)
        self.assertEqual(notes, test_status_DB.notes)
        self.assertEqual(tags, test_status_DB.tags)
        self.assertEqual(updated_by, test_status_DB.updated_by)
        self.assertEqual(bg_color, test_status_DB.bg_color)
        self.assertEqual(fg_color, test_status_DB.fg_color)

    def test_persistence_of_StatusList(self):
        """testing the persistence of StatusList
        """

        # create a couple of statuses
        statuses = [
            Status(name="Waiting To Start", code="WTS"),
            Status(name="On Hold", code="OH"),
            Status(name="In Progress", code="WIP"),
            Status(name="Complete", code="CMPLT"),
        ]

        kwargs = dict(
            name="Sequence Status List",
            statuses=statuses,
            target_entity_type="Sequence"
        )

        sequence_status_list = StatusList(**kwargs)

        DBSession.add(sequence_status_list)
        DBSession.commit()

        # store the attributes
        created_by = sequence_status_list.created_by
        date_created = sequence_status_list.date_created
        date_updated = sequence_status_list.date_updated
        description = sequence_status_list.description
        name = sequence_status_list.name
        nice_name = sequence_status_list.nice_name
        notes = sequence_status_list.notes
        statuses = sequence_status_list.statuses
        tags = sequence_status_list.tags
        target_entity_type = sequence_status_list.target_entity_type
        updated_by = sequence_status_list.updated_by

        # delete the sequence_status_list
        del sequence_status_list

        # now get it back
        sequence_status_list_DB = StatusList.query \
            .filter_by(name=kwargs["name"]) \
            .first()

        assert (isinstance(sequence_status_list_DB, StatusList))

        #self.assertEqual(sequence_status_list, sequence_status_list_DB)
        self.assertEqual(created_by, sequence_status_list_DB.created_by)
        self.assertEqual(date_created, sequence_status_list_DB.date_created)
        self.assertEqual(date_updated, sequence_status_list_DB.date_updated)
        self.assertEqual(description, sequence_status_list_DB.description)
        self.assertEqual(name, sequence_status_list_DB.name)
        self.assertEqual(nice_name, sequence_status_list_DB.nice_name)
        self.assertEqual(notes, sequence_status_list_DB.notes)
        self.assertEqual(statuses, sequence_status_list_DB.statuses)
        self.assertEqual(tags, sequence_status_list_DB.tags)
        self.assertEqual(target_entity_type,
                         sequence_status_list_DB.target_entity_type)
        self.assertEqual(updated_by, sequence_status_list_DB.updated_by)

        # try to create another StatusList for the same target_entity_type
        # and do not expect an IntegrityError

        kwargs["name"] = "new Sequence Status List"
        new_sequence_list = StatusList(**kwargs)

        DBSession.add(new_sequence_list)
        self.assertTrue(new_sequence_list in DBSession)
        self.assertRaises(IntegrityError, DBSession.commit)

    def test_persistence_of_Structure(self):
        """testing the persistence of Structure
        """
        # create pipeline steps for character
        modeling_tType = Type(
            name='Modeling',
            code='model',
            description='This is the step where all the modeling job is done',
            #created_by=admin,
            target_entity_type=Task
        )

        animation_tType = Type(
            name='Animation',
            description='This is the step where all the animation job is ' + \
                        'done it is not limited with characters, other ' + \
                        'things can also be animated',
            code='Anim',
            target_entity_type=Task
        )

        # create a new asset Type
        char_asset_type = Type(
            name='Character',
            code='char',
            description="This is the asset type which covers animated " + \
                        "characters",
            #created_by=admin,
            target_entity_type=Asset,
        )

        # get the Version Type for FilenameTemplates
        v_type = Type.query \
            .filter_by(target_entity_type="FilenameTemplate") \
            .filter_by(name="Version") \
            .first()

        # create a new type template for character assets
        assetTemplate = FilenameTemplate(
            name="Character Asset Template",
            description="This is the template for character assets",
            path="Assets/{{asset_type.name}}/{{pipeline_step.code}}",
            filename="{{asset.name}}_{{take.name}}_{{asset_type.name}}_\
            v{{version.version_number}}",
            target_entity_type="Asset",
            type=v_type
        )

        # create a new link type
        image_link_type = Type(
            name='Image',
            code='image',
            description="It is used for links showing an image",
            target_entity_type=Link
        )

        # get reference Type of FilenameTemplates
        r_type = Type.query \
            .filter_by(target_entity_type="FilenameTemplate") \
            .filter_by(name="Reference") \
            .first()

        # create a new template for references
        imageReferenceTemplate = FilenameTemplate(
            name="Image Reference Template",
            description="this is the template for image references, it "
                        "shows where to place the image files",
            #created_by=admin,
            path="REFS/{{reference.type.name}}",
            filename="{{reference.file_name}}",
            target_entity_type='Link',
            type=r_type
        )

        commercial_structure_type = Type(
            name='Commercial',
            code='commercial',
            target_entity_type=Structure
        )

        # create a new structure
        kwargs = {
            'name': 'Commercial Structure',
            'description': 'The structure for commercials',
            'custom_template': """
                Assets
                Sequences
                Sequences/{% for sequence in project.sequences %}
                {{sequence.code}}""",
            'templates': [assetTemplate, imageReferenceTemplate],
            'type': commercial_structure_type
        }

        new_structure = Structure(**kwargs)

        DBSession.add(new_structure)
        DBSession.commit()

        # store the attributes
        templates = new_structure.templates
        created_by = new_structure.created_by
        date_created = new_structure.date_created
        date_updated = new_structure.date_updated
        description = new_structure.description
        name = new_structure.name
        nice_name = new_structure.nice_name
        notes = new_structure.notes
        custom_template = new_structure.custom_template
        tags = new_structure.tags
        updated_by = new_structure.updated_by

        # delete the new_structure
        del new_structure

        new_structure_DB = DBSession.query(Structure). \
            filter_by(name=kwargs["name"]).first()

        assert (isinstance(new_structure_DB, Structure))

        self.assertEqual(templates, new_structure_DB.templates)
        self.assertEqual(created_by, new_structure_DB.created_by)
        self.assertEqual(date_created, new_structure_DB.date_created)
        self.assertEqual(date_updated, new_structure_DB.date_updated)
        self.assertEqual(description, new_structure_DB.description)
        self.assertEqual(name, new_structure_DB.name)
        self.assertEqual(nice_name, new_structure_DB.nice_name)
        self.assertEqual(notes, new_structure_DB.notes)
        self.assertEqual(custom_template, new_structure_DB.custom_template)
        self.assertEqual(tags, new_structure_DB.tags)
        self.assertEqual(updated_by, new_structure_DB.updated_by)

    def test_persistence_of_Studio(self):
        """testing the persistence of Studio
        """
        test_studio = Studio(name='Test Studio')
        DBSession.add(test_studio)
        DBSession.commit()

        # customize attributes
        test_studio.daily_working_hours = 11
        test_studio.working_hours = WorkingHours(
            working_hours={
                'mon': [],
                'sat': [[100, 1300]]
            }
        )
        test_studio.timing_resolution = datetime.timedelta(hours=1, minutes=30)

        name = test_studio.name
        daily_working_hours = test_studio.daily_working_hours
        timing_resolution = test_studio._timing_resolution
        working_hours = test_studio.working_hours

        del test_studio

        # get it back
        test_studio_DB = Studio.query.first()

        self.assertEqual(name, test_studio_DB.name)
        self.assertEqual(daily_working_hours,
                         test_studio_DB.daily_working_hours)
        self.assertEqual(timing_resolution, test_studio_DB.timing_resolution)
        self.assertEqual(working_hours, test_studio_DB.working_hours)


    def test_persistence_of_Tag(self):
        """testing the persistence of Tag
        """
        name = "Tag_test_creating_a_Tag"
        description = "this is for testing purposes"
        created_by = None
        updated_by = None
        date_created = date_updated = datetime.datetime.now()

        aTag = Tag(
            name=name,
            description=description,
            created_by=created_by,
            updated_by=updated_by,
            date_created=date_created,
            date_updated=date_updated)

        # persist it to the database
        DBSession.add(aTag)
        DBSession.commit()

        # store the attributes
        description = aTag.description
        created_by = aTag.created_by
        updated_by = aTag.updated_by
        date_created = aTag.date_created
        date_updated = aTag.date_updated

        # delete the aTag
        del aTag

        # now try to retrieve it
        aTag_DB = DBSession.query(Tag).filter_by(name=name).first()

        assert (isinstance(aTag_DB, Tag))

        self.assertEqual(name, aTag_DB.name)
        self.assertEqual(description, aTag_DB.description)
        self.assertEqual(created_by, aTag_DB.created_by)
        self.assertEqual(updated_by, aTag_DB.updated_by)
        self.assertEqual(date_created, aTag_DB.date_created)
        self.assertEqual(date_updated, aTag_DB.date_updated)


    def test_persistence_of_Task(self):
        """testing the persistence of Task
        """
        # create a task
        status1 = Status(name="stat1", code="STS1")
        status2 = Status(name="stat2", code="STS2")
        status3 = Status(name="stat3", code="STS3")
        status4 = Status(name="stat4", code="STS4")
        status5 = Status(name="stat5", code="STS5")

        task_status_list = StatusList(
            name="Task Status List",
            statuses=[status1, status2, status3, status4, status5],
            target_entity_type=Task,
        )

        project_status_list = StatusList(
            name="Project Status List",
            statuses=[status1, status2, status3, status4, status5],
            target_entity_type=Project,
        )

        asset_status_list = StatusList(
            name="Asset Status List",
            statuses=[status1, status2, status3, status4, status5],
            target_entity_type=Asset,
        )

        test_repo = Repository(
            name='Test Repo',
            linux_path='/mnt/M/JOBs',
            windows_path='M:/JOBs',
            osx_path='/Users/Shared/Servers/M',
        )

        test_project1 = Project(
            name='Tests Project',
            code='tp',
            status_list=project_status_list,
            repository=test_repo,
        )

        char_asset_type = Type(
            name='Character Asset',
            code='char',
            target_entity_type=Asset
        )

        new_asset = Asset(
            name='Char1',
            code='char1',
            status_list=asset_status_list,
            type=char_asset_type,
            project=test_project1,
        )

        user1 = User(
            name="User1",
            login="user1",
            email="user1@user.com",
            password="1234",
        )

        user2 = User(
            name="User2",
            login="user2",
            email="user2@user.com",
            password="1234",
        )

        user3 = User(
            name="User3",
            login="user3",
            email="user3@user.com",
            password="1234",
        )

        test_task = Task(
            name="Test Task",
            resources=[user1, user2],
            watchers=[user3],
            parent=new_asset,
            status_list=task_status_list,
            effort='5h',
            length='15h',
            bid='52h'
        )

        test_task.computed_start = datetime.datetime.now()
        test_task.computed_end = datetime.datetime.now() \
                                 + datetime.timedelta(10)

        DBSession.add(test_task)
        DBSession.commit()

        time_logs = test_task.time_logs
        created_by = test_task.created_by
        date_created = test_task.date_created
        date_updated = test_task.date_updated
        duration = test_task.duration
        end = test_task.end
        is_complete = test_task.is_complete
        is_milestone = test_task.is_milestone
        name = test_task.name
        priority = test_task.priority
        resources = test_task.resources
        watchers = test_task.watchers
        start = test_task.start
        status = test_task.status
        status_list = test_task.status_list
        tags = test_task.tags
        parent = test_task.parent
        type_ = test_task.type
        updated_by = test_task.updated_by
        versions = test_task.versions
        computed_start = test_task.computed_start
        computed_end = test_task.computed_end
        schedule_model = test_task.schedule_model
        schedule_timing = test_task.schedule_timing
        schedule_unit = test_task.schedule_unit

        del test_task

        # now query it back
        test_task_DB = Task.query.filter_by(name=name).first()

        assert (isinstance(test_task_DB, Task))

        self.assertEqual(time_logs, test_task_DB.time_logs)
        self.assertEqual(created_by, test_task_DB.created_by)
        self.assertEqual(computed_start, test_task_DB.computed_start)
        self.assertEqual(computed_end, test_task_DB.computed_end)
        self.assertEqual(date_created, test_task_DB.date_created)
        self.assertEqual(date_updated, test_task_DB.date_updated)
        self.assertEqual(duration, test_task_DB.duration)
        self.assertEqual(end, test_task_DB.end)
        self.assertEqual(is_complete, test_task_DB.is_complete)
        self.assertEqual(is_milestone, test_task_DB.is_milestone)
        self.assertEqual(name, test_task_DB.name)
        self.assertEqual(parent, test_task_DB.parent)
        self.assertEqual(priority, test_task_DB.priority)
        self.assertEqual(resources, test_task_DB.resources)
        self.assertEqual(start, test_task_DB.start)
        self.assertEqual(status, test_task_DB.status)
        self.assertEqual(status_list, test_task_DB.status_list)
        self.assertEqual(tags, test_task_DB.tags)
        self.assertEqual(type_, test_task_DB.type)
        self.assertEqual(updated_by, test_task_DB.updated_by)
        self.assertEqual(versions, test_task_DB.versions)
        self.assertEqual(watchers, test_task_DB.watchers)
        self.assertEqual(schedule_model, test_task_DB.schedule_model)
        self.assertEqual(schedule_timing, test_task_DB.schedule_timing)
        self.assertEqual(schedule_unit, test_task_DB.schedule_unit)

    def test_persistence_of_Ticket(self):
        """testing the persistence of Ticket
        """

        repo = Repository(
            name='Test Repository'
        )

        proj_status_list = StatusList(
            name='Project Statuses',
            statuses=[
                Status(name='Work In Progress', code='WIP'),
                Status(name='On Hold', code='OH'),
            ],
            target_entity_type='Project'
        )

        proj_structure = Structure(
            name='Commercials Structure'
        )

        proj1 = Project(
            name='Test Project 1',
            code='TP1',
            repository=repo,
            structure=proj_structure,
            status_list=proj_status_list
        )

        simple_entity = SimpleEntity(
            name='Test Simple Entity'
        )

        entity = Entity(
            name='Test Entity'
        )

        user1 = User(
            name='user 1',
            login='user1',
            email='user1@users.com',
            password='pass'
        )
        user2 = User(
            name='user 2',
            login='user2',
            email='user2@users.com',
            password='pass'
        )

        note1 = Note(content='This is the content of the note 1')
        note2 = Note(content='This is the content of the note 2')

        related_ticket1 = Ticket(project=proj1)
        DBSession.add(related_ticket1)
        DBSession.commit()

        related_ticket2 = Ticket(project=proj1)
        DBSession.add(related_ticket2)
        DBSession.commit()

        # create Tickets
        test_ticket = Ticket(
            project=proj1,
            links=[simple_entity, entity],
            notes=[note1, note2],
            reported_by=user1,
            related_tickets=[related_ticket1,
                             related_ticket2]
        )

        test_ticket.reassign(user1, user2)
        test_ticket.priority = 'MAJOR'

        DBSession.add(test_ticket)
        DBSession.commit()

        comments = test_ticket.comments
        created_by = test_ticket.created_by
        date_created = test_ticket.date_created
        date_updated = test_ticket.date_updated
        description = test_ticket.description
        links = test_ticket.links
        name = test_ticket.name
        notes = test_ticket.notes
        number = test_ticket.number
        owner = test_ticket.owner
        priority = test_ticket.priority
        project = test_ticket.project
        related_tickets = test_ticket.related_tickets
        reported_by = test_ticket.reported_by
        resolution = test_ticket.resolution
        status = test_ticket.status
        type_ = test_ticket.type
        updated_by = test_ticket.updated_by

        del test_ticket

        # now query it back
        test_ticket_DB = Ticket.query.filter_by(name=name).first()

        self.assertEqual(comments, test_ticket_DB.comments)
        self.assertEqual(created_by, test_ticket_DB.created_by)
        self.assertEqual(date_created, test_ticket_DB.date_created)
        self.assertEqual(date_updated, test_ticket_DB.date_updated)
        self.assertEqual(description, test_ticket_DB.description)
        self.assertEqual(links, test_ticket_DB.links)
        self.assertEqual(name, test_ticket_DB.name)
        self.assertEqual(notes, test_ticket_DB.notes)
        self.assertEqual(number, test_ticket_DB.number)
        self.assertEqual(owner, test_ticket_DB.owner)
        self.assertEqual(priority, test_ticket_DB.priority)
        self.assertEqual(project, test_ticket_DB.project)
        self.assertEqual(related_tickets, test_ticket_DB.related_tickets)
        self.assertEqual(reported_by, test_ticket_DB.reported_by)
        self.assertEqual(resolution, test_ticket_DB.resolution)
        self.assertEqual(status, test_ticket_DB.status)
        self.assertEqual(type_, test_ticket_DB.type)
        self.assertEqual(updated_by, test_ticket_DB.updated_by)

    def test_persistence_of_User(self):
        """testing the persistence of User
        """

        # create a new user save and retrieve it

        # create a Department for the user
        dep_kwargs = {
            "name": "Test Department",
            "description": "This department has been created for testing \
            purposes",
        }

        new_department = Department(**dep_kwargs)

        # create the user
        user_kwargs = {
            "name": "Test",
            "login": "testuser",
            "email": "testuser@test.com",
            "password": "12345",
            "description": "This user has been created for testing purposes",
            "departments": [new_department],
        }

        new_user = User(**user_kwargs)

        DBSession.add_all([new_user, new_department])
        DBSession.commit()

        # store attributes
        created_by = new_user.created_by
        date_created = new_user.date_created
        date_updated = new_user.date_updated
        departments = new_user.departments
        description = new_user.description
        email = new_user.email
        last_login = new_user.last_login
        login = new_user.login
        name = new_user.name
        nice_name = new_user.nice_name
        notes = new_user.notes
        password = new_user.password
        groups = new_user.groups
        projects = new_user.projects
        projects_lead = new_user.projects_lead
        sequences_lead = new_user.sequences_lead
        tags = new_user.tags
        tasks = new_user.tasks
        watching = new_user.watching
        updated_by = new_user.updated_by

        # delete new_user
        del new_user

        new_user_DB = DBSession.query(User) \
            .filter(User.name == user_kwargs["name"]) \
            .first()

        assert (isinstance(new_user_DB, User))

        # the user itself
        #self.assertEqual(new_user, new_user_DB)
        self.assertEqual(created_by, new_user_DB.created_by)
        self.assertEqual(date_created, new_user_DB.date_created)
        self.assertEqual(date_updated, new_user_DB.date_updated)
        self.assertEqual(departments, new_user_DB.departments)
        self.assertEqual(description, new_user_DB.description)
        self.assertEqual(email, new_user_DB.email)
        self.assertEqual(last_login, new_user_DB.last_login)
        self.assertEqual(login, new_user_DB.login)
        self.assertEqual(name, new_user_DB.name)
        self.assertEqual(nice_name, new_user_DB.nice_name)
        self.assertEqual(notes, new_user_DB.notes)
        self.assertEqual(password, new_user_DB.password)
        self.assertEqual(groups, new_user_DB.groups)
        self.assertEqual(projects, new_user_DB.projects)
        self.assertEqual(projects_lead, new_user_DB.projects_lead)
        self.assertEqual(sequences_lead, new_user_DB.sequences_lead)
        self.assertEqual(tags, new_user_DB.tags)
        self.assertEqual(tasks, new_user_DB.tasks)
        self.assertEqual(watching, new_user_DB.watching)
        self.assertEqual(updated_by, new_user_DB.updated_by)

        # as the member of a department
        department_db = DBSession.query(Department) \
            .filter(Department.name == dep_kwargs["name"]) \
            .first()

        self.assertEqual(new_user_DB, department_db.members[0])

    def test_persistence_of_Vacation(self):
        """testing the persistence of Vacation instances
        """
        # create a User
        new_user = User(
            name='Test User',
            login='testuser',
            email='test@user.com',
            password='secret'
        )

        # personal vacation type
        personal_vacation = Type(
            name='Personal',
            code='PERS',
            target_entity_type='Vacation'
        )

        start = datetime.datetime(2013, 6, 7, 15, 0)
        end = datetime.datetime(2013, 6, 21, 0, 0)

        vacation = Vacation(
            user=new_user,
            type=personal_vacation,
            start=start,
            end=end
        )

        DBSession.add(vacation)
        DBSession.commit()

        name = vacation.name

        del vacation

        # get it back
        vacation_DB = Vacation.query.filter_by(name=name).first()

        assert isinstance(vacation_DB, Vacation)
        self.assertEqual(new_user, vacation_DB.user)
        self.assertEqual(start, vacation_DB.start)
        self.assertEqual(end, vacation_DB.end)
        self.assertEqual(personal_vacation, vacation_DB.type)

    def test_persistence_of_Version(self):
        """testing the persistence of Version instances
        """

        # create a project
        test_project = Project(
            name='Test Project',
            code='tp',
            status_list=StatusList(
                name='Project Status List',
                target_entity_type=Project,
                statuses=[
                    Status(
                        name='Work In Progress',
                        code="WIP"
                    ),
                    Status(
                        name='Completed',
                        code='Cmplt'
                    )
                ]
            ),
            repository=Repository(
                name='Film Projects',
                windows_path='M:/',
                linux_path='/mnt/M/',
                osx_path='/Users/Volumes/M/',
            )
        )

        # create a task
        test_task = Task(
            name='Modeling',
            project=test_project,
            status_list=StatusList(
                name='Task Status List',
                target_entity_type=Task,
                statuses=[
                    Status(
                        name='Waiting to be Approved',
                        code='WAPP',
                    ),
                    Status(
                        name='Started',
                        code='Strt',
                    ),
                ]
            )
        )

        # create a new version
        test_version = Version(
            name='version for task modeling',
            task=test_task,
            version=10,
            take='MAIN',
            full_path='M:/Shows/Proj1/Seq1/Shots/SH001/Ligting' + \
                     '/Proj1_Seq1_Sh001_MAIN_Lighting_v001.ma',
            outputs=[
                Link(
                    name='Renders',
                    full_path='M:/Shows/Proj1/Seq1/Shots/SH001/Lighting/Output/' + \
                         'test1.###.jpg'
                ),
            ],
            status_list=StatusList(
                name='Version Statuses',
                statuses=[
                    Status(name='Status1', code='STS1'),
                    Status(name='Status2', code='STS2'),
                    Status(name='Status3', code='STS3'),
                    Status(name='Published', code='PBL')
                ],
                target_entity_type=Version,
            ),
            status=3,
        )

        # now save it to the database
        DBSession.add(test_version)
        DBSession.commit()

        created_by = test_version.created_by
        date_created = test_version.date_created
        date_updated = test_version.date_updated
        name = test_version.name
        nice_name = test_version.nice_name
        notes = test_version.notes
        outputs = test_version.outputs
        is_published = test_version.is_published
        full_path = test_version.full_path
        status = test_version.status
        status_list = test_version.status_list
        tags = test_version.tags
        take_name = test_version.take_name
        #        tickets = test_version.tickets
        type = test_version.type
        updated_by = test_version.updated_by
        version_number = test_version.version_number
        task = test_version.task

        del test_version

        # get it back from the db
        test_version_DB = Version.query.filter_by(name=name).first()

        assert (isinstance(test_version_DB, Version))

        self.assertEqual(created_by, test_version_DB.created_by)
        self.assertEqual(date_created, test_version_DB.date_created)
        self.assertEqual(date_updated, test_version_DB.date_updated)
        self.assertEqual(name, test_version_DB.name)
        self.assertEqual(nice_name, test_version_DB.nice_name)
        self.assertEqual(notes, test_version_DB.notes)
        self.assertEqual(outputs, test_version_DB.outputs)
        self.assertEqual(is_published, test_version_DB.is_published)
        self.assertEqual(full_path, test_version_DB.full_path)
        self.assertEqual(status, test_version_DB.status)
        self.assertEqual(status_list, test_version_DB.status_list)
        self.assertEqual(tags, test_version_DB.tags)
        self.assertEqual(take_name, test_version_DB.take_name)
        self.assertEqual(type, test_version_DB.type)
        self.assertEqual(updated_by, test_version_DB.updated_by)
        self.assertEqual(version_number, test_version_DB.version_number)
        self.assertEqual(task, test_version_DB.task)
   
