import tensorflow as tf
import numpy as np
class SpeechRecognition:
    def __init__(self,path):
        self.model = tf.keras.models.load_model(path)
        self.label_names=np.array(['battery', 'chew-gum', 'chocolate', 'cigaretes', 'crema',
            'lighter', 'pen', 'screwdriver', 'usb'])
    def predict(self, wav_binary):
        x=self.__get_spectogram(wav_binary)
        prediction = self.model.predict(x)
        return np.argmax(prediction[0])
    
    def __get_spectogram(self,wav_binary):
        #print(wav.shape)
        #wav = wav[16000:]
        #zero_padding = tf.zeros([16000] - tf.shape(wav), dtype=tf.float32)
        #wav = tf.concat([zero_padding, wav],0)
        wav, sample_rate = tf.audio.decode_wav(wav_binary, desired_channels=1)
        wav=wav[int(len(wav)*0.6):]
        wav = tf.squeeze(wav, axis=-1)
        spectrogram = tf.signal.stft(wav, frame_length=320, frame_step=32)
        spectrogram = tf.abs(spectrogram)
        spectrogram = tf.expand_dims(spectrogram, axis=-1)
        spectrogram= tf.image.resize_with_pad(spectrogram, 4264,257)
        spectrogram = spectrogram[tf.newaxis,...]
        
        #spectrogram = spectrogram[..., tf.newaxis]

        #print("shape")
        #print(spectrogram.shape)
        return spectrogram