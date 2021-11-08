import sys
from time import time
HEADER_SIZE = 12

class RtpPacket:	
	header = bytearray(HEADER_SIZE)
	
	def __init__(self):
		pass
		
	def encode(self, version, padding, extension, cc, seqnum, marker, pt, ssrc, payload):
		#print('RtpPacket: def encode')
		"""Encode the RTP packet with header fields and payload."""
		timestamp = int(time())
		header = bytearray(HEADER_SIZE)
		#--------------
		# TO COMPLETE
		#--------------
		# Fill the header bytearray with RTP header fields
		
		# header[0] = ...
		# ...
		# header[0] có 8 bit
		header[0] = (header[0] | version << 6) & 0xC0 # đưa 2 bit của version thành 2 bit đầu tiên, tại sao phải and 11 000 000 ? -> Solution: Tránh để bị tràn bit
		header[0] = (header[0] | padding << 5) # đưa 1 bit của padding thành bit thứ 3
		header[0] = (header[0] | extension << 4)  # đưa 1 bit extension thành bit thứ 4
		header[0] = (header[0] | (cc & 0x0F))  # tại sao phải & bit 1111 ? -> Solution: Tránh để bị tràn bit
		# header[1] = 8 bit
		header[1] = (header[1] | marker << 7) # đưa 1 bit của marker thành 1 bit thứ nhất, và ở đây ta không hê làm cc gì nữa hết ! -> Ques: tại sao không tránh trường hợp tràn bit ?
		header[1] = (header[1] | (pt & 0x7f)) # tại sao phải nhân cho 0x7f ? Để tránh tràn
		# header[2] 8 bit + header[3] 8 bit
		header[2] = (seqnum & 0xFF00) >> 8 # lấy 8 bit đầu của seq number
		header[3] = (seqnum & 0xFF) # lấy 8 bit cuối của seq number
		# header[4:8] mỗi header 8 bit -> sum= 32 bit
		header[4] = (timestamp >> 24)
		header[5] = (timestamp >> 16) & 0xFF
		header[6] = (timestamp >> 8) & 0xFF
		header[7] = (timestamp & 0xFF)
		# header[9:12] mỗi header 8 bit -> sum= 32 bit
		header[8] = (ssrc >> 24)
		header[9] = (ssrc >> 16) & 0xFF
		header[10] = (ssrc >> 8) & 0xFF
		header[11] = ssrc & 0xFF
		self.header = header
		# Get the payload from the argument
		# self.payload = ...
		self.payload = payload

	def decode(self, byteStream):
		#print('RtpPacket: def decode')
		"""Decode the RTP packet."""
		self.header = bytearray(byteStream[:HEADER_SIZE])
		self.payload = byteStream[HEADER_SIZE:]
	
	def version(self):
		#print('RtpPacket: def version')
		"""Return RTP version."""
		return int(self.header[0] >> 6)
	
	def seqNum(self):
		#print('RtpPacket: def seqNum')
		"""Return sequence (frame) number."""
		seqNum = self.header[2] << 8 | self.header[3]
		return int(seqNum)
	
	def timestamp(self):
		#print('RtpPacket: def timestamp')
		"""Return timestamp."""
		timestamp = self.header[4] << 24 | self.header[5] << 16 | self.header[6] << 8 | self.header[7]
		return int(timestamp)
	
	def payloadType(self):
		#print('RtpPacket: def payloadType')
		"""Return payload type."""
		pt = self.header[1] & 127
		return int(pt)
	
	def getPayload(self):
		#print('RtpPacket: def getPayload')
		"""Return payload."""
		return self.payload
		
	def getPacket(self):
		#print('RtpPacket: def getPacket')
		"""Return RTP packet."""
		return self.header + self.payload