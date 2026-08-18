import pytest

from app.providers.base import JobProvider


def test_job_provider_cannot_be_instantiated():
    with pytest.raises(TypeError):
        JobProvider()