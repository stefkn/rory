$(document).ready(function(){
    console.log("Client starting and attempting socketio connection.");
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/siotest');

    socket.on('newevent', function(msg) {
        parsed = JSON.parse(msg);
        console.log("Received event text" + parsed.text);
        console.log(parsed);
        if (typeof parsed.longtext === 'undefined') {
            $('#log2').html(parsed.text);
        } else {
            $('#log2').html(parsed.text);
            parsed.longtext.forEach(function (item, index) {
                $('#log').append("<li>" + item + "</li>");
            });
        }
    });

});