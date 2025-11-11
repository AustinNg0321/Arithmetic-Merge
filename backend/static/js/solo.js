async function restart() {
    const response = await fetch("/restart", { method: "POST" });
    const data = await response.json();
    document.getElementById("board").textContent = JSON.stringify(data);
}

async function move(direction) {
    const response = await fetch(`/move/${direction}`, { method: "POST" });
    const data = await response.json();
    document.getElementById("board").textContent = JSON.stringify(data);
}