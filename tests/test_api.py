import pytest

from tests.conftest import transaction


def test_health(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json['status'] == 'ok'


def test_create_persists_and_retrieve(client):
    response = client.post('/api/analyze', json=transaction())
    assert response.status_code == 201
    tid = response.json['transaction_id']
    retrieved = client.get(f'/api/transactions/{tid}')
    assert retrieved.status_code == 200
    assert retrieved.json['risk_score'] == 0
    assert retrieved.json['status'] == 'LEGITIMATE'


def test_suspicious_creation(client):
    response = client.post('/api/analyze', json=transaction(transaction_id='HIGH-001', amount=150000, location='Atlantis'))
    assert response.status_code == 201
    assert response.json['risk_score'] == 75
    assert response.json['status'] == 'SUSPICIOUS'


def test_list_transactions(client):
    client.post('/api/analyze', json=transaction())
    assert len(client.get('/api/transactions').json['transactions']) == 1


def test_missing_retrieval_is_404(client):
    assert client.get('/api/transactions/no-such-id').status_code == 404


def test_delete_existing(client):
    client.post('/api/analyze', json=transaction())
    assert client.delete('/api/transactions/TEST-001').status_code == 200
    assert client.get('/api/transactions/TEST-001').status_code == 404


def test_delete_missing(client):
    assert client.delete('/api/transactions/no-such-id').status_code == 404


def test_duplicate_id_conflict(client):
    client.post('/api/analyze', json=transaction())
    response = client.post('/api/analyze', json=transaction(amount=99))
    assert response.status_code == 409
    assert response.json['error'] == 'transaction_id already exists'


def test_missing_fields(client):
    response = client.post('/api/analyze', json={"transaction_id": "A"})
    assert response.status_code == 400
    assert 'Missing required fields' in response.json['error']


def test_malformed_json(client):
    response = client.post('/api/analyze', data='{oops', content_type='application/json')
    assert response.status_code == 400


@pytest.mark.parametrize('amount',[0,-1,'not-a-number',float('inf'),float('nan'),True])
def test_invalid_amount(client,amount):
    response=client.post('/api/analyze',json=transaction(amount=amount))
    assert response.status_code==400
    assert 'amount' in response.json['error']


def test_invalid_type(client):
    response=client.post('/api/analyze',json=transaction(transaction_type='GAMBLE'))
    assert response.status_code==400


def test_missing_content_type(client):
    assert client.post('/api/analyze',data='{}').status_code==400


def test_invalid_id_rejected(client):
    assert client.post('/api/analyze',json=transaction(transaction_id='bad id')).status_code==400
