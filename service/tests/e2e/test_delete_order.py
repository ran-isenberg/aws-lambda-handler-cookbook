import json
import uuid
from typing import Dict

import pytest
import requests

from service.models.order import Order


@pytest.fixture(scope='module')
def api_gw_url():
    import os
    url = os.environ.get('ORDER_API_GW_URL')
    if not url:
        raise ValueError('Missing environment variable: ORDER_API_GW_URL')
    return url


def test_delete_order_flow(api_gw_url):
    # First create an order to delete
    customer_name = 'E2E Test Customer'
    order_item_count = 3
    
    # Create order
    create_url = f"{api_gw_url}/api/orders/"
    create_response = requests.post(
        create_url,
        json={
            'customer_name': customer_name,
            'order_item_count': order_item_count
        }
    )
    
    assert create_response.status_code == 200
    created_order = create_response.json()
    order_id = created_order['id']
    
    # Delete the order
    delete_url = f"{api_gw_url}/api/orders/delete"
    delete_response = requests.post(
        delete_url,
        json={
            'order_id': order_id
        }
    )
    
    # Check the response
    assert delete_response.status_code == 200
    deleted_order = delete_response.json()
    assert deleted_order['id'] == order_id
    assert deleted_order['name'] == customer_name
    assert deleted_order['item_count'] == order_item_count
    
    # Try to delete the same order again, should get a 404
    delete_again_response = requests.post(
        delete_url,
        json={
            'order_id': order_id
        }
    )
    
    assert delete_again_response.status_code == 404
    assert delete_again_response.json()['error'] == 'order not found'


def test_delete_nonexistent_order(api_gw_url):
    delete_url = f"{api_gw_url}/api/orders/delete"
    nonexistent_order_id = str(uuid.uuid4())
    
    response = requests.post(
        delete_url,
        json={
            'order_id': nonexistent_order_id
        }
    )
    
    assert response.status_code == 404
    assert response.json()['error'] == 'order not found'


def test_delete_invalid_order_id(api_gw_url):
    delete_url = f"{api_gw_url}/api/orders/delete"
    
    # Test with an invalid UUID
    response = requests.post(
        delete_url,
        json={
            'order_id': 'not-a-uuid'
        }
    )
    
    # Should get a validation error
    assert response.status_code == 422