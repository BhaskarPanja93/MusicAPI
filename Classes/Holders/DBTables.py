class DBTables:
    class SONGS:
        TABLE_NAME = "songs"

        SONG_ID = "song_id"
        REAL_NAME = "real_name"
        SPOTIFY_ID = "spotify_id"
        YT_ID = "youtube_id"
        DURATION = "duration"
        THUMBNAIL = "thumbnail"
        AUDIO_URL = "audio_url"
        LAST_UPDATED = "last_updated"


    class ALIASES:
        TABLE_NAME = "aliases"

        SONG_ID = "song_id"
        STRING = "string"


    class SPOTIFY_APIS:
        TABLE_NAME = "spotify_apis"

        CLIENT_ID = "client_id"
        SECRET = "secret"
        OWNER = "owner"