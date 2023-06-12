def get_target(ctx):
    if len(ctx.message.mentions) > 0:
        return ctx.message.mentions[0]
    return ctx.message.author


def get_mention(ctx):
    if len(ctx.message.mentions) > 0:
        return ctx.message.mentions[0]
    return None
