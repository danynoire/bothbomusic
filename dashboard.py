from database import save_guild_config

@app.route("/api/control", methods=["POST"])
@login_required
def control():
    data = request.json
    gid = int(data["guild"])
    action = data["action"]
    value = data.get("value")

    async def task():
        guild = bot.get_guild(gid)
        if not guild or not guild.voice_client:
            return

        vc = guild.voice_client

        if action == "pause":
            vc.pause()
        elif action == "resume":
            vc.resume()
        elif action == "skip":
            await vc.stop()
        elif action == "seek":
            await vc.seek(int(value) * 1000)
        elif action == "volume":
            await vc.set_volume(int(value))
            save_guild_config(gid, volume=int(value))

    bot.loop.create_task(task())
    return {"ok": True}
