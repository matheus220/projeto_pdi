const setVideoSource = (source_num) => {
    let player=document.getElementById('player')
    console.log(player)
    document.getElementById('video').src = "/video_feed/" + source_num
}

var intervalID = setInterval(update_values,100);
  function update_values() {
        $.getJSON($SCRIPT_ROOT + '/toastquantity',

      function(data) {
        $('#toast_value').text(data.result);
      });
};