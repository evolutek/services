import pytest

from cellaserv.client import ReplyError
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
async def test_service(config_service, cs):
    assert await cs.config.get(section="a", option="b") == "foobar"
    assert await cs.config.get_section(section="a") == {"b": "foobar"}

    # Overwrite option
    assert await cs.config.set(section="a", option="b", value="c") is None
    assert await cs.config.get(section="a", option="b") == "c"

    # Verify that config writes to file
    assert (
        config_service.config_file_path.read_text()
        == """[a]
b = c

"""
    )

    # Test tmp set
    assert await cs.config.set_tmp(section="a", option="b", value="d") is None
    # Get returns the new value
    assert await cs.config.get(section="a", option="b") == "d"
    # Config file config has not changed
    assert (
        config_service.config_file_path.read_text()
        == """[a]
b = c

"""
    )

    # Test creating a new section
    assert await cs.config.set(section="foo", option="bar", value="test") is None
    assert await cs.config.get_section(section="foo") == {"bar": "test"}

    # Test list()
    assert await cs.config.list() == {"a": {"b": "c"}, "foo": {"bar": "test"}}

    # Test errors
    with pytest.raises(ReplyError):
        await cs.config.get(section="a", option="not_existing_option")

    with pytest.raises(ReplyError):
        await cs.config.get(
            section="not_existing_section", option="not_existing_option"
        )
