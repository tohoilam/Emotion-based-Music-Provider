const sampleRate = 16000;
blobList = [];
filenameList = [];

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
						
						var filename = new Date().toLocaleString('en-US', {
													timeZone: 'Hongkong'
												})
												.replaceAll(',', '')
												.replaceAll('/', '-')
												.replace(':', 'h')
												.replace(':', 'm');

						// Prepare the playback
						var audioObject = $('<audio controls></audio>')
								.attr('src', url);

						// Prepare the download link
						var downloadObject = $('<a>&#9660;</a>')
								.attr('href', url)
								.attr('download', filename + '.wav');
						
						let classFileName = filename.replaceAll(' ', '');
						var emotionObject = $(`<ul id="${classFileName}" class="emotion-result"></ul>`);
					

						// Wrap everything in a row
						var holderObject = $('<div class="row"></div>')
								.append(audioObject)
								.append(downloadObject)
								.append(emotionObject);

						// Append to the list
						listObject.append(holderObject);

						// fileTemp = new File([blob], filename, {
						// 	type: "audio/wav",
						// });
						blobList.push(blob);
						filenameList.push(filename)

						if (true) {
							// Bug: Can't load audio data after puttint it out to 
							try {
								context = new AudioContext({sampleRate: 16000});
								var audioBuffer = null;

								try {
									var request = new XMLHttpRequest();
									request.open('GET', url, true);
									request.responseType = 'arraybuffer';

									// Decode asynchronously
									request.onload = () => {
										context.decodeAudioData(request.response,
											(buffer) => {
												audioBuffer = buffer;
												// console.log("Duration: " + audioBuffer.duration)
												// console.log("Length: " + audioBuffer.length)
												// console.log("Channels: " + audioBuffer.numberOfChannels)
												// console.log("SR: " + audioBuffer.sampleRate)
												listAudioData.push(audioBuffer.getChannelData(0))
												listSR.push(audioBuffer.sampleRate)
											},
											(err) => {
												console.error(`Error with decoding audio data: ${err.err}`)
											}
										);
									}
									request.send();
								}
								catch(e) {
									alert('Request to retrieve audio data failed')
									console.log(e.err)
								}
							}
							catch(e) {
								alert('Web Audio API is not supported in this browser');
							}
							}
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
		var url = "http://127.0.0.1:5000/predict";

		
		var formData = new FormData();
		for (let i = 0; i < blobList.length; i++) {
			const blob = blobList[i];
			const filename = filenameList[i];

			formData.append(filename, blob, filename + '.wav');
		}
		

		$.ajax(url, {
			type: 'POST',
			dataType: 'json',
			data: formData,
			cache: false,
        	contentType: false,
        	processData: false,
		})
		.done((response) => {
			console.log(response);
			// Clear Previous Result
			$('ul.emotion-result').empty();

			// Show Predicted Result
			if (response && response.data && response.data.length > 0) {
				response.data.forEach(data => {
					let emotion = data.emotion;
					let name = data.name.replaceAll('.wav', '').replaceAll(' ', '');
					let section = data.section;
					let sectionClass = section.replaceAll(':', '').replaceAll(' ', '');
					let resultObject = $(`<ul class="${sectionClass}">${sectionClass}: ${emotion}</ul>`);
					$(`ul#${name}`).append(resultObject);

				});
			}
		})
		.fail(() => {
			console.log('Failed');
		});
	})
});
