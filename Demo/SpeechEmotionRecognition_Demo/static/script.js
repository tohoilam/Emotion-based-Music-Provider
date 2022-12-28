jQuery(document).ready(function () {
	var $ = jQuery;
	var myRecorder = {
		objects: {
			context: null,
			stream: null,
			recorder: null
		},
		init: function () {
			if (null === myRecorder.objects.context) {
				myRecorder.objects.context = new (
					window.AudioContext || window.webkitAudioContext
				);
			}
		},
		start: function () {
			var options = {audio: true, video: false};
			navigator.mediaDevices.getUserMedia(options).then(function (stream) {
				myRecorder.objects.stream = stream;
				myRecorder.objects.recorder = new Recorder(
					myRecorder.objects.context.createMediaStreamSource(stream),
					{numChannels: 1}
				);
				myRecorder.objects.recorder.record();
			}).catch(function (err) {});
		},
		stop: function (listObject) {
			if (null !== myRecorder.objects.stream) {
				myRecorder.objects.stream.getAudioTracks()[0].stop();
			}
			if (null !== myRecorder.objects.recorder) {
				myRecorder.objects.recorder.stop();

				// Validate object
				if (null !== listObject
						&& 'object' === typeof listObject
						&& listObject.length > 0) {
					// Export the WAV file
					myRecorder.objects.recorder.exportWAV(function (blob) {
						var url = (window.URL || window.webkitURL)
								.createObjectURL(blob);

						// Prepare the playback
						var audioObject = $('<audio controls></audio>')
								.attr('src', url);

						// Prepare the download link
						var downloadObject = $('<a>&#9660;</a>')
								.attr('href', url)
								.attr('download', new Date().toUTCString() + '.wav');

						// Wrap everything in a row
						var holderObject = $('<div class="row"></div>')
								.append(audioObject)
								.append(downloadObject);

						// Append to the list
						listObject.append(holderObject);
					});
				}
			}
		}
	};

	// Prepare the recordings list
	var listObject = $('[data-role="recordings"]');
	listAudioData = []
	listSR = []

	// Prepare the record button
	$('[data-role="controls"] > button').click(function () {
		// Initialize the recorder
		myRecorder.init();
		listAudioData.push('hihihih');

		// Get the button state 
		var buttonState = !!$(this).attr('data-recording');

		// Toggle
		if (!buttonState) {
			$(this).attr('data-recording', 'true');
			myRecorder.start();
		} else {
			$(this).attr('data-recording', '');
			myRecorder.stop(listObject);
		}
	});


	// Console Log Audio Data List
	$('[data-role="predict_emotion_button"]').click(() => {
		console.log(listAudioData)
		console.log(listSR)
	})
});

// jQuery(document).ready(function () {

// 	listAudioData = []
// 	listSR = []

// 	var $ = jQuery;
// 	var myRecorder = {
// 		objects: {
// 		  	context: null,
// 		  	stream: null,
// 		  	recorder: null
// 		},
// 		init: function () {
// 		  if (null === myRecorder.objects.context) {
// 			myRecorder.objects.context = new (
// 			  window.AudioContext || window.webkitAudioContext
// 			);
// 		  }
// 		},
// 		start: function () {
// 		  var options = {audio: true, video: false};
// 		  navigator.mediaDevices.getUserMedia(options).then(function (stream) {
// 			myRecorder.objects.stream = stream;
// 			myRecorder.objects.recorder = new Recorder(
// 			  myRecorder.objects.context.createMediaStreamSource(stream),
// 			  {numChannels: 1}
// 			);
// 			myRecorder.objects.recorder.record();
// 		  }).catch(function (err) {});
// 		},
// 		stop: function (listObject, listAudioData, listSR) {
// 		  if (null !== myRecorder.objects.stream) {
// 			myRecorder.objects.stream.getAudioTracks()[0].stop();
// 		  }
// 		  if (null !== myRecorder.objects.recorder) {
// 			myRecorder.objects.recorder.stop();
// 			var url = ""

// 			// Validate object
// 			if (null !== listObject
// 				&& 'object' === typeof listObject
// 				&& listObject.length > 0) {
// 			  // Export the WAV file
// 			  myRecorder.objects.recorder.exportWAV(function(blob) {
// 				var url = (window.URL || window.webkitURL)
// 						.createObjectURL(blob);

// 				// Prepare the playback
// 				var audioObject = $('<audio controls></audio>')
// 						.attr('src', url);

// 				// Prepare the download link
// 				var downloadObject = $('<a>&#9660;</a>')
// 						.attr('href', url)
// 						.attr('download', new Date().toUTCString() + '.wav');

// 				// Wrap everything in a row
// 				var holderObject = $('<div class="row"></div>')
// 						.append(audioObject)
// 						.append(downloadObject)
// 						.append(getAudioObject);


// 				// Append to the list of audio to predict
// 				listObject.append(holderObject);

// 				console.log("print!!")
// 			  });
// 			}

// 			if (true) {
// 			  // Bug: Can't load audio data after puttint it out to 
// 			  try {
// 				console.log('In try')
// 				console.log(url)

// 				context = new AudioContext();
// 				var audioBuffer = null;

// 				try {
// 				  var request = new XMLHttpRequest();
// 				  request.open('GET', url, true);
// 				  request.responseType = 'arraybuffer';

// 				  // Decode asynchronously
// 				  request.onload = () => {
// 					context.decodeAudioData(request.response,
// 					  (buffer) => {
// 						print('on load')
// 						audioBuffer = buffer;
// 						console.log("Duration: " + audioBuffer.duration)
// 						console.log("Length: " + audioBuffer.length)
// 						console.log("Channels: " + audioBuffer.numberOfChannels)
// 						console.log("SR: " + audioBuffer.sampleRate)
// 						console.log(audioBuffer.getChannelData(0))
// 						console.log(audioBuffer)

// 						listAudioData.push(audioBuffer.getChannelData(0))
// 						listSR.push(audioBuffer.sampleRate)
						
// 					  },
// 					  (err) => {
// 						console.error(`Error with decoding audio data: ${err.err}`)
// 					  } 
// 					);
// 				  }
// 				  request.send();
// 				}
// 				catch(e) {
// 				  // alert('Request to retrieve audio data failed')
// 				  console.log(e.err)
// 				}
// 			  }
// 			  catch(e) {
// 				alert('Web Audio API is not supported in this browser');
// 			  }
// 			}
// 		  }
// 		}
// 	  };

// 	  // Prepare the recordings list
// 	  var listObject = $('[data-role="recordings"]');

// 	  // Prepare the record button
// 	  $('[data-role="controls"] > button').click(function () {
// 		// Initialize the recorder
// 		myRecorder.init();
// 		listAudioData.push('hihihih');

// 		// Get the button state 
// 		var buttonState = !!$(this).attr('data-recording');

// 		// Toggle
// 		if (!buttonState) {
// 		  $(this).attr('data-recording', 'true');
// 		  myRecorder.start();
// 		} else {
// 		  $(this).attr('data-recording', '');
// 		  myRecorder.stop(listObject, listAudioData, listSR);
// 		}
// 	  });

// 	  // Console Log Audio Data LIst
// 	  $('[data-role="predict_emotion_button"]').click(() => {
// 		console.log(listAudioData)
// 		console.log(listSR)
// 	  })
// 	});