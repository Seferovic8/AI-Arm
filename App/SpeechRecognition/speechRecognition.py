import tensorflow as tf
import numpy as np
class SpeechRecognition:
    def __init__(self,path,doPath):
        self.model = tf.keras.models.load_model(path)
        self.doModel = tf.keras.models.load_model(doPath)
        print(self.model.input)
        self.command_names = np.array(['premjesti', 'dodaj' ])
        self.label_names=np.array(['battery', 'chew-gum', 'chocolate',
            'lighter', 'pen', 'screwdriver', 'usb'])
    def predict(self, wav_binary):
        x=self.__get_spectogram(wav_binary,binary=True)
        doPrediction = self.doModel.predict(x)
        x=self.__get_spectogram(wav_binary)
        objectPrediction = self.model.predict(x)
        print(self.label_names[np.argmax(objectPrediction[0])])
        return int(doPrediction<0.5),np.argmax(objectPrediction[0]),
    
    def __get_spectogram(self,wav_binary,binary=False,crop=0.35):
        #print(wav.shape)
        #wav = wav[16000:]
        #zero_padding = tf.zeros([16000] - tf.shape(wav), dtype=tf.float32)
        #wav = tf.concat([zero_padding, wav],0)
        wav, sample_rate = tf.audio.decode_wav(wav_binary, desired_channels=1)
        wav= wav[int(len(wav)*crop):] if not binary else wav[:int(len(wav)*crop)]
        wav = tf.squeeze(wav, axis=-1)
        spectrogram = tf.signal.stft(wav, frame_length=320, frame_step=32)
        spectrogram = tf.abs(spectrogram)
        spectrogram = tf.expand_dims(spectrogram, axis=-1)
        spectrogram= tf.image.resize_with_pad(spectrogram, 5365,257) if not binary else tf.image.resize_with_pad(spectrogram, 1872,257)
        spectrogram = spectrogram[tf.newaxis,...]
        
        #spectrogram = spectrogram[..., tf.newaxis]

        #print("shape")
        #print(spectrogram.shape)
        return spectrogram
