from rest_framework import status
from rest_framework.test import APITestCase
from uam_requests.models import CreateAccountRequest, AuditLog
from uam_requests import views
from faker import Faker
import factory
from random import randint
from datetime import datetime, timedelta, date
from uam_requests.management.commands import sync_audit_log
from common import utils

class CreateAccountRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CreateAccountRequest
    given_name = factory.Faker('first_name')
    surname = factory.Faker('last_name')
    account_effective_start_date = datetime.today().date()
    oa_need_windows_login = True
    ad_windows_login_name = factory.lazy_attribute(lambda a: ('%s%s' % (a.given_name, a.surname)).lower())
    oa_need_lotus_notes = True
    ln_lotus_notes_mail_name = factory.lazy_attribute(lambda a: ('%s%s' % (a.given_name, a.surname)).lower())

def _is_equal(dictionary, instance):
    for key, value in dictionary.items():
        # print(key, value)
        instance_value = getattr(instance, key, None)
        if type(instance_value) is date:
            instance_value = instance_value.strftime('%Y-%m-%d')
        if type(instance_value) is datetime:
            instance_value = instance_value.astimezone().isoformat()
        if instance_value != value:
            # print(key, instance_value, value, instance_value==value)
            return False
    return True

class TestCreateAccountRequestView(APITestCase):

    def setUp(self):
        CreateAccountRequestFactory.create_batch(10, status=CreateAccountRequest.STATUS_NEW)
        CreateAccountRequestFactory.create_batch(15, status=CreateAccountRequest.STATUS_PENDING_REVIEW_ITOO)
        CreateAccountRequestFactory.create_batch(20, status=CreateAccountRequest.STATUS_PENDING_REVIEW_ITOT)
    
    def testCreateAccountRequestViewForSubmit(self):
        init_data = CreateAccountRequest.objects.filter(status=CreateAccountRequest.STATUS_NEW)
        init_data_map = {item.id: item for item in init_data}
        ### Test for list
        response = self.client.get('/create_account_requests/prepare/')
        assert response.status_code==200
        assert len(response.data)==len(init_data)
        ### Test for single record retrieval
        randrec = response.data[randint(0,len(init_data) - 1)]
        response = self.client.get('/create_account_requests/prepare/%d/' % randrec['id'])
        assert response.status_code==200
        assert _is_equal(dict(response.data), init_data_map[randrec['id']])
        ### Test for non-exist record retrieval
        response = self.client.get('/create_account_requests/prepare/%d/' % 10000000)
        assert response.status_code==404
        ### Test for create draft
        response = self.client.post('/create_account_requests/prepare/draft/', data={}, format='json')
        assert response.status_code==201
        assert response.data['id'] is not None
        assert response.data['request_id'] is not None
        assert response.data['status'] == CreateAccountRequest.STATUS_NEW
        ### Test for submit draft
        tmp_id = response.data['id']
        response = self.client.put('/create_account_requests/prepare/%d/' % tmp_id, data={}, format='json')
        assert response.status_code==400
        # TODO... test Validation rules ....#
        # ...
        fakename = Faker().name().split()
        tmpdata = {'surname': fakename[1], 'given_name': fakename[0],
                # 'account_effective_start_date': (datetime.today().date() + timedelta(days=-1 * randint(0,100))).isoformat()
                'account_effective_start_date': 'aa',
                }
        response = self.client.put('/create_account_requests/prepare/%d/' % tmp_id, 
            data=tmpdata, format='json')
        assert response.status_code==400
        # print(response.status_code, response.data)
        tmpdata['account_effective_start_date'] = (datetime.today().date() + timedelta(days=-1 * randint(0,100))).isoformat()
        tmpdata['title'] = 'Mr.'
        response = self.client.put('/create_account_requests/prepare/%d/' % tmp_id, 
            data=tmpdata, format='json')
        # print(response.status_code, response.data)
        assert response.status_code==200
        db_obj = CreateAccountRequest.objects.get(pk=tmp_id)
        assert db_obj.status == CreateAccountRequest.STATUS_PENDING_REVIEW_ITOO
        assert _is_equal(tmpdata, db_obj)

        ### Test for create and submit together
        tmpdata = {'surname': fakename[1], 'given_name': fakename[0],
                'account_effective_start_date': (datetime.today().date() + timedelta(days=-1 * randint(0,100))).isoformat(),
                'title': 'Mrs.'
                }
        response = self.client.post('/create_account_requests/prepare/', 
            data=tmpdata, format='json')
        # print(response.status_code, response.data)
        assert response.status_code==201
        assert response.data['id'] is not None
        assert response.data['request_id'] is not None
        db_obj = CreateAccountRequest.objects.get(pk=response.data['id'])
        assert db_obj.status == CreateAccountRequest.STATUS_PENDING_REVIEW_ITOO
        assert _is_equal(tmpdata, db_obj)
        
    def testCreateAccountRequestViewForReview(self):
        init_data = CreateAccountRequest.objects.filter(status=CreateAccountRequest.STATUS_PENDING_REVIEW_ITOO)
        init_data = [rec for rec in init_data]
        init_data_map = {item.id: item for item in init_data}
        ### Test for list
        response = self.client.get('/create_account_requests/review/')
        assert response.status_code==200
        assert len(response.data)==len(init_data)
        ### Test for single record retrieval
        rand_id = randint(0,len(init_data) - 1)
        init_data_pop_rec = init_data.pop(rand_id)
        response = self.client.get('/create_account_requests/review/%d/' % init_data_pop_rec.id)
        assert response.status_code==200
        assert _is_equal(dict(response.data), init_data_pop_rec)
        ### Test for non-exist record retrieval
        response = self.client.get('/create_account_requests/review/%d/' % 10000000)
        assert response.status_code==404
        ### Test for saving draft
        rand_id = randint(0,len(init_data) - 1)
        init_data_pop_rec = init_data.pop(rand_id)
        response = self.client.put('/create_account_requests/review/%d/draft/' % init_data_pop_rec.id, data={'surname': None, 'account_effective_start_date': None}, format='json')
        assert response.status_code==200
        assert response.data['status']==CreateAccountRequest.STATUS_PENDING_REVIEW_ITOO
        assert response.data['surname']==None
        assert response.data['account_effective_start_date']==None
        ### Test for review
        ### TODO: Validation rules, duplicated windows login check ...
        response = self.client.put('/create_account_requests/review/%d/' % init_data_pop_rec.id, data={'surname': None, 'account_effective_start_date': None}, format='json')
        assert response.status_code==400
        tmp_rec= CreateAccountRequest.objects.get(pk=init_data_pop_rec.id)
        assert tmp_rec.status==CreateAccountRequest.STATUS_PENDING_REVIEW_ITOO
        response = self.client.put('/create_account_requests/review/%d/' % init_data_pop_rec.id, 
            data={'surname': 'Testing again', 'account_effective_start_date': datetime.now().date(), 'title': 'Mr.',
                'given_name': init_data_pop_rec.given_name, 'oa_need_windows_login': init_data_pop_rec.oa_need_windows_login,
                'oa_need_lotus_notes': init_data_pop_rec.oa_need_lotus_notes,
            },
            format='json')
        assert response.status_code==200
        tmp_rec= CreateAccountRequest.objects.get(pk=init_data_pop_rec.id)
        assert tmp_rec.status==CreateAccountRequest.STATUS_PENDING_REVIEW_ITOT
        ### Test for reject
        rand_id = randint(0,len(init_data) - 1)
        init_data_pop_rec = init_data.pop(rand_id)
        ### TODO: Validation rules ...
        response = self.client.put('/create_account_requests/review/%d/reject/' % init_data_pop_rec.id, format='json')
        # print(response.status_code, response.data)
        assert response.status_code==400
        response = self.client.put('/create_account_requests/review/%d/reject/' % init_data_pop_rec.id, 
            data={'oth_other_justification': 'Hello'},
            format='json')
        assert response.status_code==200
        tmp_rec= CreateAccountRequest.objects.get(pk=init_data_pop_rec.id)
        assert tmp_rec.status==CreateAccountRequest.STATUS_REJECTED_BY_ITOO

    def testCreateAccountRequestViewForExecute(self):
        init_data = CreateAccountRequest.objects.filter(status=CreateAccountRequest.STATUS_PENDING_REVIEW_ITOT)
        init_data = [rec for rec in init_data]
        init_data_map = {item.id: item for item in init_data}
        ### Test for list
        response = self.client.get('/create_account_requests/execute/')
        assert response.status_code==200
        assert len(response.data)==len(init_data)
        ### Test for single record retrieval
        rand_id = randint(0,len(init_data) - 1)
        init_data_pop_rec = init_data.pop(rand_id)
        response = self.client.get('/create_account_requests/execute/%d/' % init_data_pop_rec.id)
        assert response.status_code==200
        assert _is_equal(dict(response.data), init_data_pop_rec)
        ### Test for non-exist record retrieval
        response = self.client.get('/create_account_requests/execute/%d/' % 10000000)
        assert response.status_code==404
        ### Test for saving draft
        rand_id = randint(0,len(init_data) - 1)
        init_data_pop_rec = init_data.pop(rand_id)
        response = self.client.put('/create_account_requests/execute/%d/draft/' % init_data_pop_rec.id, data={'surname': None, 'account_effective_start_date': None}, format='json')
        assert response.status_code==200
        assert response.data['status']==CreateAccountRequest.STATUS_PENDING_REVIEW_ITOT
        assert response.data['surname']==None
        assert response.data['account_effective_start_date']==None
        ### Test for review
        ### TODO: Validation rules, duplicated windows login check ...
        response = self.client.put('/create_account_requests/execute/%d/' % init_data_pop_rec.id, data={'surname': None, 'account_effective_start_date': None}, format='json')
        assert response.status_code==400
        tmp_rec= CreateAccountRequest.objects.get(pk=init_data_pop_rec.id)
        assert tmp_rec.status==CreateAccountRequest.STATUS_PENDING_REVIEW_ITOT
        response = self.client.put('/create_account_requests/execute/%d/' % init_data_pop_rec.id, 
            data={'surname': 'Testing again', 'account_effective_start_date': datetime.now().date(), 'title': 'Mr.',
                'given_name': init_data_pop_rec.given_name, 'oa_need_windows_login': init_data_pop_rec.oa_need_windows_login,
                'oa_need_lotus_notes': init_data_pop_rec.oa_need_lotus_notes,
            },
            format='json')
        assert response.status_code==200
        tmp_rec= CreateAccountRequest.objects.get(pk=init_data_pop_rec.id)
        assert tmp_rec.status==CreateAccountRequest.STATUS_COMPLETED
        assert tmp_rec.related_user is not None
        for field_name in tmp_rec.get_clone_field_list():
            assert getattr(tmp_rec, field_name, None) == getattr(tmp_rec.related_user, field_name, None)
        assert tmp_rec.related_user.uam_id is not None
        assert tmp_rec.related_user.ad_sync_time is None
        assert tmp_rec.related_user.notes_sync_time is None
        ### Test for reject
        rand_id = randint(0,len(init_data) - 1)
        init_data_pop_rec = init_data.pop(rand_id)
        ### TODO: Validation rules ...
        response = self.client.put('/create_account_requests/execute/%d/reject/' % init_data_pop_rec.id, format='json')
        assert response.status_code==400
        response = self.client.put('/create_account_requests/execute/%d/reject/' % init_data_pop_rec.id, 
            data={'oth_other_remark': 'Hello'},
            format='json')
        assert response.status_code==200
        tmp_rec= CreateAccountRequest.objects.get(pk=init_data_pop_rec.id)
        assert tmp_rec.status==CreateAccountRequest.STATUS_REJECTED_BY_ITOT

    def test_audit_log(self):
        fakename = Faker().name().split()
        audit_log_init_len = AuditLog.objects.count()
        tmpdata = {'surname': fakename[1], 'given_name': fakename[0],
                'title': 'Mr.',
                'account_effective_start_date': (datetime.today().date() + timedelta(days=-1 * randint(0,100))).isoformat(),
                'oa_need_windows_login': True,
                'oa_need_lotus_notes': True,
                'ad_windows_login_name': ''.join(fakename),
                'ln_lotus_notes_mail_name': ''.join(fakename)
                }
        response = self.client.post('/create_account_requests/prepare/', 
            data=tmpdata, format='json')
        # print(response.status_code, response.data)
        assert response.status_code==201
        request_id = response.data['request_id']
        tmp_id = response.data['id']
        assert audit_log_init_len + 1 == AuditLog.objects.count()

        response = self.client.put('/create_account_requests/review/%d/' % tmp_id, 
            data=tmpdata, format='json')
        assert response.status_code==200
        assert audit_log_init_len + 2 == AuditLog.objects.count()

        response = self.client.put('/create_account_requests/execute/%d/' % tmp_id, 
            data=tmpdata, format='json')
        assert response.status_code==200
        assert audit_log_init_len + 3 == AuditLog.objects.count()

        oldlog = utils.get_request_log(request_id)
        test_command = sync_audit_log.Command()
        test_command.handle()
        newlog = utils.get_request_log(request_id)
        assert len(newlog) - 3 == len(oldlog)

        response = self.client.get('/audit_log/request/%s/' % request_id)
        assert response.status_code==200
        assert type(response.data) is list
        assert len(response.data) == len(newlog)
