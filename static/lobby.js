if (parseInt(isHost) === parseInt(lobbyId)) {
    showStartButton();
}

const socket = new WebSocket(`ws://127.0.0.1:8000/ws/joinLobby/`);
socket.onopen = function() {
    socket.send(JSON.stringify(
        {
            value: 'connecting', 
            lobbyId: lobbyId
        }
    ));
    console.log("Połączono z WebSocket");
}

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);

    if (data.type === "players") {
        const playersList = document.getElementById("players");
        playersList.innerHTML = "";
        if (data.host === parseInt(userId)) {
            data.players.forEach(player => {
                const li = document.createElement("li");
                if (player.isHost) {
                    li.innerText = 'host: ' + player.username;
                } else {
                    li.innerText = player.username;
                }

                if (player.id !== parseInt(userId)) {
                    const kickBtn = document.createElement("button");
                    kickBtn.innerText = "Kick";
                    kickBtn.style.marginLeft = "10px";

                    kickBtn.onclick = function() {
                        socket.send(JSON.stringify({
                            value: "kickPlayer",
                            playerId: player.id,
                            lobbyId: lobbyId
                        }));
                    };

                    li.appendChild(kickBtn);
                }

                playersList.appendChild(li);
            })
        } else {
            data.players.forEach(player => {
                const li = document.createElement("li");
                if (player.isHost) {
                    li.innerText = 'host: ' + player.username;
                } else {
                    li.innerText = player.username;
                }
                playersList.appendChild(li);
            });
        }
    } else if (data.type === 'startGame') {
        if (isHost === lobbyId) {
            window.location.href = `http://127.0.0.1:8000/game/${lobbyId.toString()}`;
        } else {
            window.location.href = `http://127.0.0.1:8000/join-game/${lobbyId.toString()}`;
        }
    } else if (data.type === 'kickPlayer') {
        window.location.href = 'http://127.0.0.1:8000/';
    } else if (data.type === 'newHost') {
        if (data.newHostId === parseInt(userId)) {
            showStartButton();
            isHost = lobbyId
        }
    } else if (data.type === 'gameIsOn') {
        document.getElementById('isGameOn').innerText = 'Game is on, wait till the end';
    } else if (data.type === 'gameIsEnded'){
        document.getElementById('isGameOn').innerText = '';
    }
};

socket.onclose = function() {
    console.log("Połączenie zakończone");
};

socket.onerror = function(err) {
    console.error("WebSocket error:", err);
};


function showStartButton() {
    if (document.getElementById('startGame')) return;

    const controls = document.getElementById('controls');

    const timeSelection = document.createElement('select');
    timeSelection.id = 'timeSelection';

    [30, 60, 90].forEach(time => {
        const option = document.createElement('option');
        option.value = time;
        option.textContent = time + " s";
        timeSelection.appendChild(option);
    });

    const btn = document.createElement('button');
    btn.id = 'startGame';
    btn.innerText = 'Start Game';

    btn.onclick = function() {

        const selectedTime = document.getElementById('timeSelection').value;

        console.log('startGame', selectedTime);

        socket.send(JSON.stringify({
            value: 'startGame',
            lobbyId: lobbyId,
            time: selectedTime
        }));
    };

    controls.appendChild(timeSelection);
    controls.appendChild(btn);
}