function send(action, value = null) {
  const buttons = document.querySelectorAll("button")
  buttons.forEach(b => b.disabled = true)

  fetch("/api/control", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      guild: GUILD_ID,
      action: action,
      value: value
    })
  }).finally(() => {
    setTimeout(() => {
      buttons.forEach(b => b.disabled = false)
      refresh()
    }, 300)
  })
}

function refresh() {
  fetch(`/api/state/${GUILD_ID}`)
    .then(r => r.json())
    .then(d => {
      const track = document.getElementById("track")
      track.classList.remove("pulse")
      track.innerText = d.track || "Nada tocando"
      track.classList.add("pulse")

      const queue = document.getElementById("queue")
      queue.innerHTML = ""

      if (d.queue) {
        d.queue.forEach(t => {
          const li = document.createElement("li")
          li.textContent = t
          queue.appendChild(li)
        })
      }
    })
}

setInterval(refresh, 1500)
