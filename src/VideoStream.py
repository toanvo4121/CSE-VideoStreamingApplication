class VideoStream:
	def __init__(self, filename):
		self.filename = filename
		try:
			self.file = open(filename, 'rb')
		except:
			raise IOError
		self.frameNum = 0
		self.isNext = 0
		self.totalFrame = 0

		print('frame = 0')

	def get_total_time_video(self):
		self.totalFrame=0
		while True:
			data = self.file.read(5)
			if data:
				framelength = int(data)
				# Read the current frame
				data = self.file.read(framelength)
				self.totalFrame += 1
			else:
				self.file.seek(0)
				break
			totalTime = self.totalFrame * 0.05
		return totalTime

	def setIsNext(self):
		self.isNext = 1

	def nextFrame(self):
		"""Get next frame."""
		if self.isNext == 1:
			forwardFrames = int(self.totalFrame*0.1)
			remainFrames = int(self.totalFrame - self.frameNum)
			if forwardFrames > remainFrames:
				forwardFrames = remainFrames
			self.isNext = 0

		else:
			forwardFrames = 1
		if forwardFrames:
			for i in range(forwardFrames):
				data = self.file.read(5) # Get the framelength from the first 5 bits
				if data:
					framelength = int(data)

					# Read the current frame
					data = self.file.read(framelength)
					self.frameNum += 1
			return data

	def prevFrame(self):
		preFrames = int(self.totalFrame * 0.1)
		if self.frameNum <= preFrames:
			data = self.file.seek(0)
			self.frameNum = 0
			if data:
				framelength = int(data)
				# Read the current frame
				data = self.file.read(framelength)
				self.frameNum += 1
		else:
			data = self.file.seek(0)
			fFrames = self.frameNum - preFrames
			self.frameNum = 0
			for i in range(fFrames):
				data = self.nextFrame()

		return data

	def frameNbr(self):
		"""Get frame number."""
		return self.frameNum

	
	