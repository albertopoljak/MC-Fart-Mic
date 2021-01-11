GITHUB_REPO_LINK = "https://github.com/albertopoljak/MC-Fart-Mic"
PROGRAM_VERSION = 0.4

# Formats that are sure to be supported on all backends, depending on user OS many more might be supported.
SURE_SUPPORTED_AUDIO_FORMATS = ("mp3", "wav")

# Possible audio formats
POSSIBLE_AUDIO_FORMATS: set = {
    "3gp", "aac", "aiff", "ape", "au", "flac", "m4a", "m4b", "m4p", "mpc", "ogg", "oga", "opus", "wma", "webm",
    "avi",
    *SURE_SUPPORTED_AUDIO_FORMATS
}
