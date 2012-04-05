===
VLC
===

Command used to launch VLC's streaming server on the URI http://streaminghost.com:8081/stream.ogg

vlc -I rc ~/path/to/music.mp3 ":sout=#transcode{vcodec=theo,vb=800,scale=1,acodec=vorb,ab=128,channels=2,samplerate=44100}:http{dst=:8081/stream.ogg}" :sout-keep
