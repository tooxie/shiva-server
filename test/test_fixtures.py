"""
Very simple test fixture tests. Consider them placeholders for
regression tests.
Domain specific tests should have their own test module.
"""

def test_media_dirs(media_dirs):
    assert len(media_dirs) == 2


def test_app(app):
    assert len(app.config['MEDIA_DIRS']) == 2