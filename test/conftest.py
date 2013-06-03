import pytest
from shiva.media import MediaDir


@pytest.fixture
def media_dirs(tmpdir):
    # how to touch files via py.path.local
    # http://py.readthedocs.org/en/latest/path.html#checking-path-types

    # TODO depending on extension, create correct music file based on a
    # wav or something

    foo = tmpdir.mkdir('foo')
    foo.join('bar.mp3').ensure(file=True)
    foo.join('baz.mp3').ensure(file=True)
    qoo = tmpdir.mkdir('qoo')
    qoo.join('qux.ogg')

    return [
        MediaDir(foo.strpath),
        MediaDir(qoo.strpath)
    ]


@pytest.fixture
def app(media_dirs):
    from shiva.app import app
    app.config['MEDIA_DIRS'] = media_dirs
    return app