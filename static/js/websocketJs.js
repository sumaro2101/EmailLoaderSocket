$(document).ready(function() {
    const pk = JSON.parse($('#email_id').text());
    const socket = new WebSocket(
        'ws://'
        + window.location.host
        + '/email/download/'
        + pk
        + '/'
    );
    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if ('reverse_number' in data) {
            var count = data.count;
            var reverse_number = data.reverse_number;
            var procent = data.procent;
            var title = data.title.slice(0, 10) + '...';
            var sender = data.sender;
            var date_sending = data.date_sending;
            var date_receipt = data.date_receipt;
            var text = data.text;
            var files = data.files;
            if (text != null) {
                var text = text.slice(0, 200) + '...';
            };
            var array_values = [title, sender, date_sending, date_receipt, text, files];
            var th = $('<th scope="row"></th>').text(count);
            var tr = $('<tr></tr>').append(th).attr('id', count);
            $('.table tbody').prepend(tr);
            for (var k = 0; k < array_values.length; k++) {
                var td = $('<td></td>').text(array_values[k]).addClass('text-wrap lh-1 text-break').css('font-size', '12px');
                $('#' + count).append(td);
            };
            $('.loads').text(reverse_number);
            $('.progress').attr('aria-valuenow', procent);
            $('.progress-bar').css('width', procent + '%');
            if (procent == 100.00) {
                $('.status').text('Done!')
                this.close()
            };
        };

        if ('list_uids' in data) {
            $('.progress-bar').css('width', '0%');
            $('.progress').attr('aria-valuenow', 0);
            var wait = $('.wait');
            var status = $('.status');
            status.text('Read...');
            var list_uids = data.list_uids.reverse();
            var length_uids = list_uids.length;
            for (var j = 1; j <= length_uids; j++) {
                wait.text(j);
            };
            status.text('Load...');
            if (length_uids == 0) {
                status.text('No data to load yet')
                this.close()
            }
        }
        for (var i = 0; i <= length_uids - 1; i++) {
            socket.send(JSON.stringify({
                'uid': list_uids[i],
            }));
    };
    };

    socket.onclose = function(e) {
        this.close()
        console.log('Socket closed unexpectedly');
    };
});