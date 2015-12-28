import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5

class ChatAudio(object):
	def __init__(self):
		self.arg = None

	def Record(self):
		p = pyaudio.PyAudio()
		stream = p.open(format=FORMAT,
		                channels=CHANNELS,
		                rate=RATE,
		                input=True,
		                frames_per_buffer=CHUNK)

		print("* recording")
		frames = []
		for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
		    data = stream.read(CHUNK)
		    frames.append(data)
		print("* done recording")
		stream.stop_stream()
		stream.close()
		p.terminate()
		return frames

	def ToString(self,frames):
		data=''
		FrameCount = len(frames)
		for i in range(0,FrameCount):
			data=data+str(frames[i])
		return data

	
	def Play(self,AudioString):
		p = pyaudio.PyAudio()
		stream = p.open(format=FORMAT,
		                channels=CHANNELS,
		                rate=RATE,
		                output=True)
		stream.write(AudioString)
		stream.stop_stream()
		stream.close()
		p.terminate()
