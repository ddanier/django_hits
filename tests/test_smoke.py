import pytest


def test_smoke():
    """Just some basic smoke tests (syntax, app loading)"""
    import django_hits
    import django_hits.models
    import django_hits.utils
    import django_hits.templatetags.hit_tags


def test_system_checks():
    import django

    if django.VERSION >= (1, 7, 0):
        from django.core import checks

        if django.VERSION >= (1, 8, 0):
            assert not checks.run_checks(include_deployment_checks=False), "Some Django system checks failed"
        else:
            assert not checks.run_checks(), "Some Django system checks failed"


@pytest.mark.django_db
def test_db():
    pass  # makes sure migrations are run
