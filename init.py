from discord import opus, Intents

OPUS_LIBS = [
    "/usr/local/lib/libopus.0.dylib",
    "/usr/local/lib/libopus.so.0",
]


def load_opus_lib(opus_libs=OPUS_LIBS):
    if opus.is_loaded():
        return True

    for opus_lib in opus_libs:
        try:
            opus.load_opus(opus_lib)
            return
        except:
            pass


def intents():
    intents = Intents.default()
    intents.voice_states, intents.guild_messages, intents.guilds = True, True, True
    intents.message_content = True
    return intents
