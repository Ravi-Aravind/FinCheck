import pytest

from tests.conftest import transaction


@pytest.mark.parametrize('field,value',[('transaction_id',''),('transaction_id','x'*65),('location',''),('location','x'*81),('transaction_type','payment')])
def test_invalid_strings(client,field,value):
    response=client.post('/api/analyze',json=transaction(**{field:value}))
    assert response.status_code==400
    assert 'error' in response.json


def test_non_object_json_rejected(client):
    response=client.post('/api/analyze',json=[])
    assert response.status_code==400
