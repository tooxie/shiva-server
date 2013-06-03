def test_media_dirs(media_dirs):
    assert len(media_dirs) == 2


def test_app(app):
    assert len(app.config['MEDIA_DIRS']) == 2