from shiva.media import MediaDir


def test_media_dir(media_dirs):
    hiphop = media_dirs[0]
    assert isinstance(hiphop, MediaDir)
    dirs = hiphop.get_dirs()

    assert dirs[0].endswith('Erykah Badu')
    assert dirs[1].endswith('RJD2')
    # excluded not listed but available
    assert not [True for x in dirs if x.endswith('Videos')]
    assert hiphop.exclude[0].endswith('Videos')
