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