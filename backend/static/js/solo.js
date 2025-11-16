document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("up").addEventListener("click", () => move("up"));
    document.getElementById("down").addEventListener("click", () => move("down"));
    document.getElementById("left").addEventListener("click", () => move("left"));
    document.getElementById("right").addEventListener("click", () => move("right"));

    document.getElementById("restart").addEventListener("click", () => restart());
});

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