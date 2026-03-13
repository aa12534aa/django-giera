const socket = new WebSocket(`ws://127.0.0.1:8000/ws/results/`) 

socket.onopen = function() {
    socket.send(JSON.stringify(
        {lobbyId: lobbyId}
    ));
}

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);

    if (data.type === 'timer') {
        document.getElementById('timer').innerHTML = data.time;
    } else if (data.type === 'backToLobby') {
        window.location.href = `http://127.0.0.1:8000/lobby/${data.lobbyId.toString()}`;
    }
}

const scoreTable = document.getElementById('scoreTable');
scoreTable.innerHTML = '';

players.sort(function(b, a){return a.score - b.score});
let i = 1;
players.forEach(player => {
    const row = document.createElement("div");
    row.style.display = "flex";
    row.style.gap = "10px";

    const place = document.createElement("h2");
    place.innerText = i;
    i += 1;

    const playerName = document.createElement("h2");
    playerName.innerText = player.username + ':';

    const playerScore = document.createElement("h2");
    playerScore.innerText = player.score;

    row.appendChild(place);
    row.appendChild(playerName);
    row.appendChild(playerScore);

    scoreTable.appendChild(row);
});

