# vim: set fileencoding=utf-8 filetype=python :
import pytest
from shiva.media import MediaDir


@pytest.fixture
def media_dirs(tmpdir):
    """
    Creates a directory structure as follows in a temporary directory::

        /tmp/pytest-29/test_media_dir0/
        ├── Hip-Hop
        │   ├── Erykah Badu
        │   │   ├── Baduizm (2003)
        │   │   │   ├── 01 - Rimshot (Intro).ogg
        │   │   │   ├── 02 - On & On.ogg
        │   │   │   ├── 03 - Appletree.ogg
        │   │   │   ├── 04 - Otherside Of The Game.ogg
        │   │   │   ├── 05 - Sometimes (Mix %239).ogg
        │   │   │   ├── 06 - Next Lifetime.ogg
        │   │   │   ├── 07 - Afro (Freestyle Skit).ogg
        │   │   │   ├── 08 - Certainly.ogg
        │   │   │   ├── 09 - 4 Leaf Clover.ogg
        │   │   │   ├── 10 - No Love.ogg
        │   │   │   ├── 11 - Drama.ogg
        │   │   │   ├── 12 - Sometimes.ogg
        │   │   │   ├── 13 - Certainly (Flipped It).ogg
        │   │   │   └── 14 - Rimshot (Outro).ogg
        │   │   └── Worldwide Underground (2003)
        │   │       ├── 01 - Intro - World Keeps Turnin'.ogg
        │   │       ├── 02 - Bump It.ogg
        │   │       ├── 03 - Back In The Day.ogg
        │   │       ├── 04 - I Want You.ogg
        │   │       ├── 05 - Woo.ogg
        │   │       ├── 06 - The Grind.ogg
        │   │       ├── 07 - Danger.ogg
        │   │       ├── 08 - Think Twice.ogg
        │   │       ├── 09 - Love Of My Life Worldwide.ogg
        │   │       ├── 10 - Outro - World Keeps Turnin'.ogg
        │   │       └── 11 - Love Of My Life (An Ode To Hip Hop).ogg
        │   ├── RJD2
        │   │   ├── Since We Last Spoke (2004)
        │   │   │   ├── 01 - Since We Last Spoke.ogg
        │   │   │   ├── 02 - Exotic Talk.ogg
        │   │   │   ├── 03 - 1976.ogg
        │   │   │   ├── 04 - Ring Finger.ogg
        │   │   │   ├── 05 - Making Days Longer.ogg
        │   │   │   ├── 06 - Someone's Second Kiss.ogg
        │   │   │   ├── 07 - To All of You.ogg
        │   │   │   ├── 08 - Clean Living.ogg
        │   │   │   ├── 09 - Iced Lightning.ogg
        │   │   │   ├── 10 - Intro.ogg
        │   │   │   ├── 11 - Through the Walls.ogg
        │   │   │   ├── 12 - One Day.ogg
        │   │   │   ├── 13 - De L'alouette.ogg
        │   │   │   └── 14 - Holy Toledo.ogg
        │   │   └── The Horror (2003)
        │   │       ├── 01 - The Horror.ogg
        │   │       ├── 02 - Ghostwriter Remix.ogg
        │   │       ├── 03 - Final Frontier Remix.ogg
        │   │       ├── 04 - Bus Stop Bitties.ogg
        │   │       ├── 05 - Good Times Roll Pt. 1.ogg
        │   │       ├── 06 - Sell The World.ogg
        │   │       ├── 07 - June Remix.ogg
        │   │       ├── 08 - Counseling Inst.ogg
        │   │       ├── 09 - Final Frontier Inst.ogg
        │   │       └── 10 - F.H.H Inst.ogg
        │   └── Videos
        │       └── Sade - Live (2011).avi
        └── Jazz
            └── Diana Krall
                └── When I look In Your Eyes (1999)
                    ├── 01 - Let`s Face the Music and Dance.ogg
                    ├── 02 - Devil May Care.ogg
                    ├── 03 - Let`s Fall in Love.ogg
                    ├── 04 - When I Look in Your Eyes.ogg
                    ├── 05 - Popsicle Toes.ogg
                    ├── 06 - I`ve Got You Under My Skin.ogg
                    ├── 07 - I Can`t Give You Anything But.ogg
                    ├── 08 - I`ll String Along With You.ogg
                    ├── 09 - East of the Sun (and West of t.ogg
                    ├── 10 - Pick Yourself Up.ogg
                    ├── 11 - The Best Thing for You.ogg
                    ├── 12 - Do It Again.ogg
                    └── 13 - Why Should I Care (Bonus Track.ogg

        11 directories, 63 files


    This comment and the code are highly redundant. It would be cool if we
    could parse a tree like structure as above into test files. For now::

        tree /tmp/pytest-<NUM>/test_media_dirs0/

    :param tmpdir: py.path.local
    :return:
    """

    # how to touch files via py.path.local
    # http://py.readthedocs.org/en/latest/path.html#checking-path-types

    # TODO depending on extension, create correct music file based on a
    # wav or something

    HipHop = tmpdir.mkdir("Hip-Hop")

    Erykah_Badu = HipHop.mkdir("Erykah Badu")

    Baduizm = Erykah_Badu.mkdir("Baduizm (2003)")
    Baduizm.join("01 - Rimshot (Intro).ogg").ensure(file=True)
    Baduizm.join("02 - On & On.ogg").ensure(file=True)
    Baduizm.join("03 - Appletree.ogg").ensure(file=True)
    Baduizm.join("04 - Otherside Of The Game.ogg").ensure(file=True)
    Baduizm.join("05 - Sometimes (Mix %239).ogg").ensure(file=True)
    Baduizm.join("06 - Next Lifetime.ogg").ensure(file=True)
    Baduizm.join("07 - Afro (Freestyle Skit).ogg").ensure(file=True)
    Baduizm.join("08 - Certainly.ogg").ensure(file=True)
    Baduizm.join("09 - 4 Leaf Clover.ogg").ensure(file=True)
    Baduizm.join("10 - No Love.ogg").ensure(file=True)
    Baduizm.join("11 - Drama.ogg").ensure(file=True)
    Baduizm.join("12 - Sometimes.ogg").ensure(file=True)
    Baduizm.join("13 - Certainly (Flipped It).ogg").ensure(file=True)
    Baduizm.join("14 - Rimshot (Outro).ogg").ensure(file=True)

    WorldwideUnderground = Erykah_Badu.mkdir("Worldwide Underground (2003)")
    WorldwideUnderground.join("01 - Intro - World Keeps Turnin'.ogg") \
        .ensure(file=True)
    WorldwideUnderground.join("02 - Bump It.ogg").ensure(file=True)
    WorldwideUnderground.join("03 - Back In The Day.ogg").ensure(file=True)
    WorldwideUnderground.join("04 - I Want You.ogg").ensure(file=True)
    WorldwideUnderground.join("05 - Woo.ogg").ensure(file=True)
    WorldwideUnderground.join("06 - The Grind.ogg").ensure(file=True)
    WorldwideUnderground.join("07 - Danger.ogg").ensure(file=True)
    WorldwideUnderground.join("08 - Think Twice.ogg").ensure(file=True)
    WorldwideUnderground.join("09 - Love Of My Life Worldwide.ogg").ensure(
        file=True)
    WorldwideUnderground.join("10 - Outro - World Keeps Turnin'.ogg").ensure(
        file=True)
    WorldwideUnderground.join(
        "11 - Love Of My Life (An Ode To Hip Hop).ogg").ensure(file=True)

    RJD2 = HipHop.mkdir('RJD2')

    TheHorror = RJD2.mkdir('The Horror (2003)')
    TheHorror.join("01 - The Horror.ogg").ensure(file=True)
    TheHorror.join("02 - Ghostwriter Remix.ogg").ensure(file=True)
    TheHorror.join("03 - Final Frontier Remix.ogg").ensure(file=True)
    TheHorror.join("04 - Bus Stop Bitties.ogg").ensure(file=True)
    TheHorror.join("05 - Good Times Roll Pt. 1.ogg").ensure(file=True)
    TheHorror.join("06 - Sell The World.ogg").ensure(file=True)
    TheHorror.join("07 - June Remix.ogg").ensure(file=True)
    TheHorror.join("08 - Counseling Inst.ogg").ensure(file=True)
    TheHorror.join("09 - Final Frontier Inst.ogg").ensure(file=True)
    TheHorror.join("10 - F.H.H Inst.ogg").ensure(file=True)

    SinceWeLastSpoke = RJD2.mkdir("Since We Last Spoke (2004)")
    SinceWeLastSpoke.join("01 - Since We Last Spoke.ogg").ensure(file=True)
    SinceWeLastSpoke.join("02 - Exotic Talk.ogg").ensure(file=True)
    SinceWeLastSpoke.join("03 - 1976.ogg").ensure(file=True)
    SinceWeLastSpoke.join("04 - Ring Finger.ogg").ensure(file=True)
    SinceWeLastSpoke.join("05 - Making Days Longer.ogg").ensure(file=True)
    SinceWeLastSpoke.join("06 - Someone's Second Kiss.ogg").ensure(file=True)
    SinceWeLastSpoke.join("07 - To All of You.ogg").ensure(file=True)
    SinceWeLastSpoke.join("08 - Clean Living.ogg").ensure(file=True)
    SinceWeLastSpoke.join("09 - Iced Lightning.ogg").ensure(file=True)
    SinceWeLastSpoke.join("10 - Intro.ogg").ensure(file=True)
    SinceWeLastSpoke.join("11 - Through the Walls.ogg").ensure(file=True)
    SinceWeLastSpoke.join("12 - One Day.ogg").ensure(file=True)
    SinceWeLastSpoke.join("13 - De L'alouette.ogg").ensure(file=True)
    SinceWeLastSpoke.join("14 - Holy Toledo.ogg").ensure(file=True)

    Videos = HipHop.mkdir('Videos')
    Videos.join("Sade - Live (2011).avi").ensure(file=True)

    Jazz = tmpdir.mkdir('Jazz')

    DianaKrall = Jazz.mkdir('Diana Krall')
    WhenIlookInYourEyes = DianaKrall.mkdir('When I look In Your Eyes (1999)')
    WhenIlookInYourEyes.join("01 - Let`s Face the Music and Dance.ogg").ensure(
        file=True)
    WhenIlookInYourEyes.join("02 - Devil May Care.ogg").ensure(file=True)
    WhenIlookInYourEyes.join("03 - Let`s Fall in Love.ogg").ensure(file=True)
    WhenIlookInYourEyes.join("04 - When I Look in Your Eyes.ogg").ensure(
        file=True)
    WhenIlookInYourEyes.join("05 - Popsicle Toes.ogg").ensure(file=True)
    WhenIlookInYourEyes.join("06 - I`ve Got You Under My Skin.ogg").ensure(
        file=True)
    WhenIlookInYourEyes.join("07 - I Can`t Give You Anything But.ogg").ensure(
        file=True)
    WhenIlookInYourEyes.join("08 - I`ll String Along With You.ogg").ensure(
        file=True)
    WhenIlookInYourEyes.join("09 - East of the Sun (and West of t.ogg").ensure(
        file=True)
    WhenIlookInYourEyes.join("10 - Pick Yourself Up.ogg").ensure(file=True)
    WhenIlookInYourEyes.join("11 - The Best Thing for You.ogg").ensure(
        file=True)
    WhenIlookInYourEyes.join("12 - Do It Again.ogg").ensure(file=True)
    WhenIlookInYourEyes.join("13 - Why Should I Care (Bonus Track.ogg").ensure(
        file=True)

    return [
        MediaDir(root=HipHop.strpath, dirs=(Erykah_Badu.strpath,
                                            RJD2.strpath),
                 exclude=Videos.strpath),
        MediaDir(Jazz.strpath)
    ]


@pytest.fixture
def app(media_dirs):
    from shiva.app import app

    app.config['MEDIA_DIRS'] = media_dirs
    return app
