const socket = new WebSocket(`ws://127.0.0.1:8000/ws/game/`);

socket.onopen = function() {
    socket.send(JSON.stringify(
        {value: 'prepareGame', lobbyId: lobbyId}
    ));
    console.log('Connected');

    socket.send(JSON.stringify(
        {value: 'startTimer', lobbyId: lobbyId}
    ));
}

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.type === 'wordsForGame') {
        const words = document.getElementById('words');
        data.wordsList.forEach(word => {
            words.textContent += word + ' ';
        });
    } else if (data.type === 'timer'){
        document.getElementById('timer').innerHTML = data.time;
    } else if (data.type === 'endGame') {
        window.location.href = `http://127.0.0.1:8000/lobby/${data.lobbyId.toString()}`;
    }
}