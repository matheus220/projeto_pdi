const setVideoSource = (source_num) => {
    let player=document.getElementById('player')
    console.log(player)
    document.getElementById('video').src = "/video_feed/" + source_num
}