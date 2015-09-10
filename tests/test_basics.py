import pytest
from django_hits.models import Hit
from django.contrib.auth.models import AnonymousUser


@pytest.mark.django_db
def test_simple_hit():
    hit = Hit.objects.hit('something', None, '127.0.0.1')
    assert hit.views == 1
    assert hit.visits == 1
    hit = Hit.objects.hit('something', None, '127.0.0.1')
    assert hit.views == 2
    assert hit.visits == 1
