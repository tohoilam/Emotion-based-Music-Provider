const sampleRate = 16000;
const domain = 'http://127.0.0.1:5000'
blobList = [];
filenameList = [];

jQuery(document).ready(function () {
	var $ = jQuery;

	$.ajax(domain + '/models', {
		type: 'GET',
		dataType: 'json',
	})
	.done((response) => {
		if (response && response.data && response.data.length > 0) {
			response.data.forEach(data => {
				let optionObject = $(`<option value=${data.id}>${data.name}</option>`);
				$('#model-selection').append(optionObject);
			})
		}
	})
	.fail(() => {
		console.log('Failed');
	});

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
						var filename = new Date().toLocaleString('en-US', {
																	timeZone: 'Hongkong'
																})
																.replaceAll(',', '')
																.replaceAll('/', '-')
																.replace(':', 'h')
																.replace(':', 'm');
						
						addAudioRow(filename + '.wav', blob);
					});
				}
			}
		}
	};

	// Prepare the recordings list
	var listObject = $('[data-role="recordings"]');

	// Prepare the record button
	$('[data-role="controls"] > button').click(function (e) {
		e.preventDefault();
		e.stopPropagation();

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
	$('[data-role="predict-emotion-button"]').click((e) => {
		e.preventDefault();
		e.stopPropagation();

		const url = domain + "/predict";

		const modelChoice = $('#model-selection').val();
		
		var formData = new FormData();
		formData.append('modelChoice', modelChoice);
		for (let i = 0; i < blobList.length; i++) {
			const blob = blobList[i];
			const filename = filenameList[i];
			const filenameNoExtension = filename.substring(0, filename.indexOf('.'));

			formData.append(filenameNoExtension, blob, filename);
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
			// Clear Previous Result
			$('ul.emotion-result').empty();

			// Show Predicted Result
			if (response && response.data && response.data.length > 0) {
				response.data.forEach(data => {
					let emotion = data.emotion;
					let name = data.name.replaceAll('.wav', '').replaceAll(' ', '-');
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

	// File Upload Section
	$('#upload-form').click((e) => {
		e.preventDefault();
		e.stopPropagation();

		$('#file-input').trigger('click');
	})

	$('#file-input').change((e) => {
		e.preventDefault();
		e.stopPropagation();

		console.log('hi');
		console.log(e.target.files);
		if (e.target.files && e.target.files.length > 0) {
			const files = e.target.files;
			storeFiles(files);
		}
	})

	 // preventing page from redirecting
	 $("#upload-form").on("dragover", e => {
		e.preventDefault();
		e.stopPropagation();
		
	 });
	
	 $("#upload-form").on("drop", e => {
		e.preventDefault();
		e.stopPropagation();
		console.log('drop');

		const files = e.originalEvent.dataTransfer.files;
		storeFiles(files);
	});

	var storeFiles = (files) => {
		for (let i = 0; i < files.length; i++) {
			const file = files[i];
			// if (file.type != 'audio/wav' || file.type != 'audio/x-m4a' || file.type != 'audio/mpeg'  || file.type != 'audio/ogg')
			if (file.type !== 'audio/wav' && file.type !== 'audio/x-m4a'
				&& file.type !== 'audio/mpeg' && file.type !== 'audio/ogg'
				&& file.type !== 'audio/basic') {
				console.log("Please only upload .wav, .m4a, .mp3, .ogg, .opus, or .au file type!");
			}
			else {
				// let dateName = new Date().toLocaleString('en-US', {
				// 												timeZone: 'Hongkong'
				// 											})
				// 											.replaceAll(',', '')
				// 											.replaceAll('/', '-')
				// 											.replace(':', 'h')
				// 											.replace(':', 'm');
				
				// let filename = file.name.substring(file.name.indexOf('.'));
				// filename = dateName + filename;
				addAudioRow(file.name, file);
			}
		}
	}

	var addAudioRow = (filename, blob) => {
		var url = (window.URL || window.webkitURL)
				.createObjectURL(blob);

		// Prepare the playback
		var audioObject = $('<audio controls></audio>')
				.attr('src', url);

		// Prepare the download link
		var downloadObject = $('<a>&#9660;</a>')
				.attr('href', url)
				.attr('download', filename);
		
		let classFileName = filename.replaceAll(' ', '-');
		classFileName = classFileName.substring(0, classFileName.indexOf('.'));
		var emotionObject = $(`<ul id="${classFileName}" class="emotion-result"></ul>`);
	

		// Wrap everything in a row
		var holderObject = $('<div class="audio-row"></div>')
				.append(audioObject)
				.append(downloadObject)
				.append(emotionObject);

		// Append to the list
		listObject.append(holderObject);

		blobList.push(blob);
		filenameList.push(filename);
	}
});
