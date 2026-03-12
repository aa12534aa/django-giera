const socket = new WebSocket(`ws://127.0.0.1:8000/ws/game/`);

socket.onopen = function() {
    socket.send(JSON.stringify(
        {value: 'prepareGame', lobbyId: lobbyId}
    ));

    socket.send(JSON.stringify(
        {value: 'startTimer', lobbyId: lobbyId}
    ));
}

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.type === 'createScoreTable') {
        const scoreTable = document.getElementById('scoreTable');
        scoreTable.innerHTML = '';
        data.playersAndScore.forEach(player => {
            console.log(player)
            const row = document.createElement("div");
            row.style.display = "flex";
            row.style.gap = "10px";

            const playerName = document.createElement("h4");
            playerName.innerText = player.username + ':';

            const playerScore = document.createElement("h4");
            playerScore.id = 'player' + player.username;
            playerScore.innerText = '0';

            row.appendChild(playerName);
            row.appendChild(playerScore);

            scoreTable.appendChild(row);
        })
    } else if (data.type === 'updateScoreTable') {
        console.log(data.player);
        const playerToUpdate = document.getElementById('player' + data.player);
        playerToUpdate.innerText = parseInt(playerToUpdate.innerText) + 1;
    } else if (data.type === 'wordsForGame') {
        const words = document.getElementById('words');
        words.innerHTML = '';
        let wordId = 0;
        data.wordsList.forEach(word => {
            const h3 = document.createElement("h3");
            h3.id = 'word' + wordId;
            h3.innerText = word;
            h3.style.marginRight = "10px";
            h3.style.marginBottom = "-5px";
            words.appendChild(h3);
            wordId += 1;
        });
    } else if (data.type === 'timer'){
        document.getElementById('timer').innerHTML = data.time;
    } else if (data.type === 'correctWord') {
        const element = document.getElementById('word' + data.wordId)
        element.style.color = 'green';
    } else if (data.type === 'endGame') {
        window.location.href = `http://127.0.0.1:8000/results/${data.lobbyId.toString()}`;
    }
}

document.getElementById('playerWordForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const word = document.getElementById('playerWord').value;
    document.getElementById('playerWord').value = '';

    socket.send(JSON.stringify(
        {value: 'playerWord', word: word, lobbyId: lobbyId}
    ))
})