import pytest

from cellaserv.client import ReplyError
from cellaserv.examples.fixtures import proxy
from evolutek.services.config import Config


@pytest.fixture
async def config_service(tmp_path):
    config_file = tmp_path / "config.ini"
    config_file.write_text(
        """
[a]
b = foobar
"""
    )

    service = Config(config_file=config_file)
    await service.ready()
    yield service
    await service.kill()


@pytest.mark.asyncio
async def test_service(config_service, proxy):
    assert await proxy.config.get(section="a", option="b") == "foobar"
    assert await proxy.config.get_section(section="a") == {"b": "foobar"}

    # Overwrite option
    assert await proxy.config.set(section="a", option="b", value="c") is None
    assert await proxy.config.get(section="a", option="b") == "c"

    # Verify that config writes to file
    assert (
        config_service.config_file_path.read_text()
        == """[a]
b = c

"""
    )

    # Test tmp set
    assert await proxy.config.set_tmp(section="a", option="b", value="d") is None
    # Get returns the new value
    assert await proxy.config.get(section="a", option="b") == "d"
    # Config file config has not changed
    assert (
        config_service.config_file_path.read_text()
        == """[a]
b = c

"""
    )

    # Test creating a new section
    assert await proxy.config.set(section="foo", option="bar", value="test") is None
    assert await proxy.config.get_section(section="foo") == {"bar": "test"}

    # Test list()
    assert await proxy.config.list() == {"a": {"b": "c"}, "foo": {"bar": "test"}}

    # Test errors
    with pytest.raises(ReplyError):
        await proxy.config.get(section="a", option="not_existing_option")

    with pytest.raises(ReplyError):
        await proxy.config.get(
            section="not_existing_section", option="not_existing_option"
        )
