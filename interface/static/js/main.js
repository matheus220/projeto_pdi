const setVideoSource = (source_num) => {
    let player=document.getElementById('player')
    console.log(player)
    document.getElementById('video').src = "/video_feed/" + source_num
    var intervalID = setInterval(update_values,100);
}
function update_values() {
    $.getJSON($SCRIPT_ROOT + '/quantity',

  function(data) {
    $('#toast_count').text(data.toastCount);
    $('#total_value').text(data.totalCount);
    $('#speed_value').text(data.speedValue);
    $('#toast_value').text(data.toastValue);
    $('#alpha_value').text(data.alpha);
  });
};