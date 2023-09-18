# Emotion-based Music Provider (Machine Learning Side)
 
## Project Overview
A machine learning and web application project that recommends and generates music for users based on their emotions expressed from speech input. The project is separated into 3 major components:

1. <ins>**Speech Emotion Recognition:**</ins> Detects emotion from speech with acoustic and text analyses
2. <ins>**Music Recommendation:**</ins> Recommends the most relevant existing song given a certain emotion
3. <ins>**Music Generation:**</ins> Generates new symbolic music pieces given certain emotion

<img src="https://github.com/tohoilam/Emotion-based-Music-Provider-Application/assets/61353084/edc8845c-d391-4b56-8fa2-91396b099c8f" alt="Project Overview" width="600"/>

**NOTE:** This repository is dedicated to the machine learning side of the project. If you would like to view the web application side GitHub page, please [click here](https://github.com/tohoilam/Emotion-based-Music-Provider-Application).


### Important Links
* [Web Application Side GitHub Page](https://github.com/tohoilam/Emotion-based-Music-Provider-Application)
* [YouTube Short Introduction](https://www.youtube.com/watch?v=1yL7BDyDFCM)

## Speech Emotion Recognition

A CNN-LSTM model for Speech Emotion Recognition is trained and optimized from scratch with Keras.

#### Input
The input of the model is a 251x128 mel-spectrogram of an 8-second audio. Speech audio is first split at each 8-second, remaining last audio section with less than 2 seconds is discarded, otherwise, padding is added to span the audio to 8 seconds. Then each 8-second speech audio is transformed into a Mel-spectrogram through a Short-time Fourier Transform (STFT). The transformation methods and split duration are chosen after experimenting with other alternatives.

#### Layer Structure

The model is a combination of Convolutional Neural Networks (CNN) and Long Short-term Memory (LSTM) models, giving CNN-LSTM. The first four layers are alternating Convolutional, Batch Normalization, and Max-Pooling layers, capturing the high-level features from the Mel-spectrogram input of speech audio. Followed by a Bi-directional LSTM layer after reshaping into a one-dimensional array, which captures the time-dependency information of a speech audio. All hyperparameters and layer structures are chosen after hundreds of iterations of experiments.


#### Output

In order to match the music emotion classification task in music recommendation, the output is generalized into 4 emotions:
* Anger
* Happiness
* Neutral
* Sadness


![Final CNN-LSTM Model](https://github.com/tohoilam/Emotion-based-Music-Provider/assets/61353084/387685e5-f140-4f9b-af07-da2bf57ecb32)

### Results

As a result, we achieved a validation accuracy of 0.71 and a testing accuracy of 0.62. With the confusion matrix shown below

<img src="https://github.com/tohoilam/Emotion-based-Music-Provider/assets/61353084/09b765d1-816c-4165-b8f0-11979d854681" alt="SER Confusion Matrix" width="400"/>


## Music Recommendation

Music recommendation is done through 3 different analyses:
* <ins>**Acoustic Emotion Analysis:**</ins> Analysing the emotion expressed through your voice (tones, pitch, etc.) and the music
* <ins>**Text Emotion Analysis:**</ins> Analysing the emotion expressed from the user's speech and song lyrics
* <ins>**Semantics Analysis:**</ins> Analysing the meanings of user's speech and song lyrics

### The 3 Analyses

The Music Emotion Recognition (MER) section of the system aims to classify the emotion of songs. The system used 2 approaches to classify music emotion: Acoustic Music Emotion Recognition and Text Emotion Detection (TED). 

1. The Acoustic MER approach uses deep learning techniques to predict the Valence Arousal (VA) value of the music from its acoustic features. The TED approach analyzes the emotion of the lyrics. Keywords are also extracted to provide further information about the song. The final Acoustic MER model uses two 64 LSTM layers followed by a 64 dense layer and an output layer. The final TED model has an eight-layer structure, including an encoding layer, an embedding layer, two Bi-LSTM layers, a dropout layer, an extra dense layer, a dropout layer, and finally an output layer.
2. For Text Emotion Detection (TED), the final model is a 5-layer Bidirectional LSTM model, with 6 layers including an encoding layer, an embedding layer, two Bi-LSTM layers, a dropout layer, and finally an output layer. Kera’s TextVectorizer was used as the encoder to convert sentences into a series of numbers, which were then passed to the embedding layer, transforming the input into fixed-size vectors, and applying masking. The vectors are then passed into the two Bi-directional LSTM layers to learn time-dependent features and then output to the dense layer for classification. (Note: TED task is also done on the speech side in order for a valid comparison between text emotion. However, two separate models are trained for the speech side and the music side)

Furthermore, Semantics analysis is used to further improve the relevance of suggested songs. First, keywords and their significance are extracted from lyrics and the user's speech respectively. The KeyBERT keyword extraction model is used in this stage.

### Mapping between speech side and music side

Information about the emotions of the user is retrieved from and provided by the SER section of the system. The emotion percentage from the Acoustic-based SER will be compared with the VA value of the song retrieved by the Acoustic MER from the acoustic music of the song. On the other hand, the results from the Text-based SER will be compared with the emotion percentage predicted of the song predicted by TED from the lyrics of the song. Finally, through semantics analysis, the similarities between every keyword from the user's speech and the song lyrics are compared. 

**The overall relevance score is computed by the weighted similarity scores of each keyword pair based on their significance.**

### The Song List

A set of songs must be selected for the system. To create such a dataset, songs are selected based on the information from Genius and Spotify. The final application includes a total of 4519 songs, as well as the corresponding music emotion values and extracted keywords predicted from the MER and the keyword extraction process.

![Recommendation Flowchart](https://github.com/tohoilam/Emotion-based-Music-Provider/assets/61353084/e4c290d3-7801-41b6-b222-5d8dd70df406)



## Music Generation

We focused on two types of music generation, monophonic and polyphonic generation. In monophonic music generation, at most 1 note is allowed within a time step, while multiple notes are allowed in polyphonic music generation.

To generate music of the four emotions, four separate models were trained independently, which represent different emotions. The training data were first classified by our symbolic Music Emotion Recognition (MER) to obtain an emotion label. Then it is fitted into corresponding models after preprocessing and feature extraction. A primer of corresponding emotion will be selected as input.  The symbolic MER model is also used to verify the emotion of generated music. If it fails to pass the test, a different primer will be selected for re-generation.

### Model Structure

In music generation model training, we made use [Magenta](https://github.com/magenta/magenta)'s [melodyRNN](https://github.com/magenta/magenta/tree/main/magenta/models/melody_rnn) for training.

For symbolic MER, an 8-layer Multilayer Perceptron (MLP) model is used, with 3 hidden layers and alternating dropout layers in between. The model is trained with 14 music-related features

For Monophonic Music Generation, we adopted the Attention RNN model from Magenta. Attention RNN is a double-layered LSTM model with an attention mask. Given a preceding note sequence, the model will suggest the following notes based on the probability distribution and combine all generated notes to become a music piece. In addition, this model is capable of recognizing the melody of the music by introducing the attention mask and specific features.

For Polyphonic Music Generation, we adopted the Polyphonic RNN model from Magenta. Similar to Attention RNN, Polyphonic RNN is a multi-layered LSTM model. Although it can handle multiple notes with a single time step, it does not contain extra information regarding melody structure.


![Generation Flowchart](https://github.com/tohoilam/Emotion-based-Music-Provider/assets/61353084/df07a660-7e6e-45f1-bfc5-e25ca9a4809a)


<!---
[![Spotify](https://spotify-github-readme.vercel.app/api/spotify)](https://open.spotify.com/collection/tracks)
-->
