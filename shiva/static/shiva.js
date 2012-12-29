Shiva = {};

// Base {{{
buzz.sound.prototype.destroy = function() {
    this.set('src', '');
};

Shiva.Collection = Backbone.Collection.extend({
    server_url: '',
    url: function() {
        return this.server_url + this.resource_url;
    },
    play: function() {
        this.get('player').play();
    },
    stop: function() {
        this.get('player').destroy();
    },
    pause: function() {
        this.get('player').stop();
    }
});

Shiva.Audio = function(audio_url) {
    server_url = '';
    return {
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
            this.track.destroy();
        },

        pause: function() {
            this.track.stop();
        }
    }
}

Shiva.Routes = Backbone.Router.extend({
    routes: {
        '': 'artistList',
        'artists': 'artistList',
        'artist/:artistId': 'artistDetail'
    },

    initialize: function(app) {
        this.app = app;
    },

    artistList: function() {
        console.log('artist list');
        $('#content').html('<ul id="artists"></ul>');
        app.renderArtists();
    },

    artistDetail: function(artistId) {
        console.log('artist detail');
        $('#content').html('<ul id="albums"></ul>');
        var artistModel = app.artists.get(artistId);
        artistModel.each(function(el) {
            var AlbumView = new Shiva.AlbumView({
                model: el.get('album'),
                id: artistModel.get('hash')
            });
            $('#albums').append(artistView.render());
        });
    }
});
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
    },
    render: function() {
        return '<li>' + this.model.get('title') + '</li>';
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

Shiva.ArtistView = Backbone.View.extend({
    el: '#artists',
    tagName: 'li',
    className: 'artist',
    render: function() {
        var artistId = this.model.get('id');
        var artistName = this.model.get('name');
        return '' +
            '<li class="artist">' +
                '<a href="#/artist/' + artistId + '" id="artist_' + artistId + '">' + artistName + '</a>' +
            '</li>';
    }
});
// }}}
