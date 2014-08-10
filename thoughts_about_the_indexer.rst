Indexer Modes
=============
Concerning metadata, there are three basic indexer modes:


Minimal Mode
------------
Given the ``--nometadata`` flag, the indexer operates in "minimal" mode.

It gets paths from configured MediaDirs and add tracks to the DB containing
only path and date_added (which are not nullable).
All we need to do is to *traverse* the MediaDirs and their child
*directories*. No files need to be opened / read.

Afterwards, we have a list of paths in our DB.

This is quite fast.


Local Metadata Mode
-------------------
If no flag is given, we not only traverse the MediaDirs, but we
read *every* file. The opening happens indirectly through Mutagen which
reads the file's metadata. This takes a little while, because Mutage needs
to convert the file header information into a python data structure. That's
also what uses quite some CPU time.


LastFM
------
We use lastfm to get cover images by artist and album name.


Conclusion
----------
Minimal is a prerequisite for local which in turn is a prerequisite
for LastFM. I think the architecture should reflect that, so here's my
proposal (pseudo code)::

    track_models = run_minimal()
    db.save(track_models)

    if nometadata:
        return

    track_models_with_meta = run_local(track_models)
    db.save(track_models_with_meta)

    if not lastfm:
        return

    track_models_with_covers = run_lastfm(track_models_with_meta)
    db.save(track_models_with_covers)

This would make multiprocessing much easier.

It would also enable us to run those parts separately. Just imagine a::

    models.Track.query.all()

before the single step.

