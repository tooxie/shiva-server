// Base {{{
Shiva.Collection = Backbone.Collection.extend({
    server_url: 'http://localhost:5001/api',
    url: function() {
        return this.server_url + this.resource_url;
    },
    play: function() {
        this.get('player').play();
    },
    stop: function() {
        this.get('player').stop();
    }
});

Shiva.Audio = function(audio_url) {
    return {
        server_url: 'http://localhost:5001/api',

        url: function() {
            return this.server_url + audio_url;
        },

        load_track: function() {
            if (this.track === undefined) {
                this.track = new buzz.sound(this.url(), {
                    formats: ['mp3', 'ogg']
                });
            };
        },

        play: function() {
            this.load_track();
            this.track.play();
        },

        stop: function() {
            this.load_track();
            this.track.stop();
        }
    }
}
// }}}


// Tracks {{{
Shiva.Track = Backbone.Model.extend({
    initialize: function() {
        this.set({
            'player': new Shiva.Audio(this.get('download_uri'))
        })
    }
});

Shiva.TrackList = Shiva.Collection.extend({
    model: Shiva.Track,
    resource_url: '/tracks'
});
// }}}


// Albums {{{
Shiva.Album = Backbone.Model.extend({
    initialize: function() {
        /* TODO: Define a player for each model (Album and Artist) that would
         * fetch (lazy) and play all of the tracks for that given model.
         */
        this.set({
            'tracks': []
        });
        this.set({
            'player': new Shiva.Audio(this.get('download_uri'))
        })
    }
});

Shiva.AlbumList = Shiva.Collection.extend({
    model: Shiva.Album,
    resource_url: '/albums'
});
// }}}


// Artists {{{
Shiva.Artist = Backbone.Model.extend({
    // Nothing
});

Shiva.ArtistList = Shiva.Collection.extend({
    model: Shiva.Artist,
    resource_url: '/artists'
});
// }}}
