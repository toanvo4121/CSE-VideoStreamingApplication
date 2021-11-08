from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os
import datetime
from RtpPacket import RtpPacket
import time

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"

class Client2:
    INIT = 0
    READY = 1
    PLAYING = 2
    state = INIT

    SETUP = 0
    PLAY = 1
    PAUSE = 2
    TEARDOWN = 3
    DESCRIBE = 4
    FORWARD = 5
    PREV= 6

    checkSocketIsOpen = False
    checkPlay = False
    isFirstPlay= True
    counter = 0

    # Initiation..
    def __init__(self, master, serveraddr, serverport, rtpport, filename):
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.handler)

        self.serverAddr = serveraddr
        self.serverPort = int(serverport)
        self.rtpPort = int(rtpport)
        self.fileName = filename
        self.rtspSeq = 0
        self.sessionId = 0
        self.requestSent = -1
        self.teardownAcked = 0
        self.connectToServer()
        self.currentTime = 0
        self.frameNbr = 0
        self.totalTime = 0

        self.isForward = 0
        self.isBackward = 0
        self.createWidgets()

        # statistical data

        self.countTotalPacket = 0
        self.timerBegin = 0
        self.timerEnd = 0
        self.timer = 0
        self.bytes = 0
        self.packets = 0
        self.packetsLost = 0
        self.lastSequence = 0
        self.totalJitter = 0
        self.arrivalTimeofPreviousPacket = 0
        self.lastPacketSpacing = 0
        

        #self.setupMovie()

    def createWidgets(self):
        """Build GUI."""
        # Create Play button
        self.start = Button(self.master, width=15, padx=3, pady=3)
        self.start["text"] = "Play ▶"
        self.start["bg"] = "#56ff6d"
        self.start["fg"] = "black"
        self.start["command"] = self.playMovie
        self.start.grid(row=2, column=0, padx=2, pady=2)

        # Create Pause button
        self.pause = Button(self.master, width=15, padx=3, pady=3)
        self.pause["text"] = "Pause ⏸"
        self.pause["bg"] = "#f8ed54"
        self.pause["fg"] = "black"
        self.pause["command"] = self.pauseMovie
        self.pause.grid(row=2, column=1, padx=2, pady=2)

        # Create Teardown button
        self.stop = Button(self.master, width=15, padx=3, pady=3)
        self.stop["text"] = "Stop ■"
        self.stop["command"] = self.resetMovie
        self.stop["bg"]= "#e05927"
        self.stop["fg"] = "black"
        self.stop.grid(row=2, column=2, padx=2, pady=2)

        # Create Setup button
        self.describe = Button(self.master, width=15, padx=3, pady=3)
        self.describe["text"] = "Describe ★"
        self.describe["command"] = self.describeMovie
        self.describe["bg"] = "#409dfa"
        self.describe["fg"] = "black"
        self.describe["state"] = "disabled"
        self.describe.grid(row=2, column=3, padx=2, pady=2)

        # Create a label to display the movie
        self.label = Label(self.master, height=18, bg= "#A5D2EB")
        self.label.grid(row=0, column=0, columnspan=5, sticky=W + E + N + S, padx=5, pady=5)

        # Create a label to display total time of the movie
        self.totaltimeBox = Label(self.master, width=16, text="Total time: 00:00", bg= "#A5D2EB")
        self.totaltimeBox.grid(row=1, column=3, columnspan=1, padx=5, pady=5)

        # Create a label to display remaining time of the movie

        self.remainTimeBox = Label(self.master, width=16, text="Remaining time: 00:00", bg="#A5D2EB")
        self.remainTimeBox.grid(row=1, column=0, columnspan=1, padx=5, pady=5)

        # Create forward button
        self.forward = Button(self.master, width=15, padx=3, pady=3, bg= "#00EBC1", fg= "black")
        self.forward["text"] = "⫸⫸"
        self.forward["command"] = self.forwardMovies
        self.forward["state"] = "disabled"
        self.forward.grid(row=1, column=2, padx=2, sticky= E + W, pady=2)

        # Create backward button
        self.backward = Button(self.master, width=15, padx=3, pady=3, bg= "#00EBC1", fg= "black")
        self.backward["text"] = "⫷⫷"
        self.backward["command"] = self.prevMovie
        self.backward["state"] = "disabled"
        self.backward.grid(row=1, column=1, sticky = E + W, padx=2, pady=2)



    def describeMovie(self):
        """Describe button handler"""
        self.sendRtspRequest(self.DESCRIBE)

    def setupMovie(self):
        """Setup button handler."""
        if self.state == self.INIT:
            self.sendRtspRequest(self.SETUP)

    def resetMovie(self):
        """Teardown button handler."""
        if self.checkPlay:
            self.checkPlay = False
            self.sendRtspRequest(self.TEARDOWN)
            try:
                for i in os.listdir():
                    if i.find(CACHE_FILE_NAME) == 0:
                        os.remove(i)
            except:
                pass
            time.sleep(1)
            self.forward["state"] = "disabled"
            self.backward["state"] = "disabled"
            self.rtspSeq = 0
            self.sessionId = 0
            self.requestSent = -1
            self.teardownAcked = 0
            self.counter = 0
            self.isFirstPlay = True
            self.isForward = 0
            self.isBackward = 0
            self.currentTime = 0
            # if not (self.checkSocketIsOpen):
            self.connectToServer()
            self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.label.pack_forget()
            self.label.image = ''
            # time.sleep(0.5)
            # self.setupMovie()

    def pauseMovie(self):
        """Pause button handler."""
        if self.state == self.PLAYING:
            self.forward["state"]= "disabled"
            self.backward["state"] = "disabled"
            self.sendRtspRequest(self.PAUSE)


    def playMovie(self):
        """Play button handler."""
        if self.state == self.INIT and self.isFirstPlay == True:
            self.isFirstPlay = False
            self.checkPlay = True
            self.frameNbr = 0
            self.countTotalPacket = 0
            self.timerBegin = 0
            self.timerEnd = 0
            self.timer = 0
            self.bytes = 0
            self.packets = 0
            self.packetsLost = 0
            self.lastSequence = 0
            self.totalJitter = 0
            self.arrivalTimeofPreviousPacket = 0
            self.lastPacketSpacing = 0
            self.setupMovie()
            while self.state != self.READY:
                pass

        self.forward["state"] = "normal"
        self.backward["state"] = "normal"
        self.describe["state"] = "normal"

        if self.state == self.READY:
            self.checkPlay = True
            # Create a new thread to listen for RTP packets
            threading.Thread(target=self.listenRtp).start()
            self.playEvent = threading.Event()
            self.playEvent.clear()
            self.sendRtspRequest(self.PLAY)

    def forwardMovies(self):
        self.sendRtspRequest(self.FORWARD)
        self.isForward = 1

    def prevMovie(self):
        self.sendRtspRequest(self.PREV)
        if self.frameNbr <= 50:
            self.frameNbr = 0
        else:
            self.frameNbr -= 50
        self.isBackward = 1

    def listenRtp(self):
        """Listen for RTP packets."""
        while True:
            try:
                data = self.rtpSocket.recv(20480)
                if data:

                    rtpPacket = RtpPacket()
                    rtpPacket.decode(data)

                    # currFrameNbr = rtpPacket.seqNum()
                    arrivalTimeOfPacket = time.perf_counter()
                    print("Current Seq Num: " + str(rtpPacket.seqNum()))
                    self.bytes += len(rtpPacket.getPacket())
                    try:
                        if (self.frameNbr + 1 != rtpPacket.seqNum()) & (not(self.isForward | self.isBackward)):
                            print('count: ',self.counter)
                            self.counter += 1
                            print('=' * 100 + "\n\nMat Goi\n\n" + '=' * 100)
                        currFrameNbr = rtpPacket.seqNum()
                        self.currentTime = int(currFrameNbr * 0.05)
                        # Update remaining time
                        self.totaltimeBox.configure(text="Total time: %02d:%02d" % (self.totalTime // 60, self.totalTime % 60))
                        self.remainTimeBox.configure(text="Remaining time: %02d:%02d" % ((self.totalTime - self.currentTime)// 60, (self.totalTime - self.currentTime) % 60))
                    # version = rtpPacket.version()


                    except:
                        print("seqNum() Loi \n")
                        traceback.print_exc(file=sys.stdout)
                        print("\n")
                    if currFrameNbr > self.frameNbr:  # Discard the late packet
                        self.frameNbr = currFrameNbr
                        self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
                        # statUpdate
                        self.countTotalPacket += 1
                        self.packets += 1
                        self.packetsLost += currFrameNbr - self.lastSequence - 1
                        # calculate total jitter
                        if self.lastSequence == currFrameNbr - 1 and currFrameNbr > 1:
                            interPacketSpacing = arrivalTimeOfPacket - self.arrivalTimeofPreviousPacket
                            jitterIncrement = abs(interPacketSpacing - self.lastPacketSpacing)
                            self.totalJitter = self.totalJitter + jitterIncrement
                            self.lastPacketSpacing = interPacketSpacing

                        self.arrivalTimeofPreviousPacket = arrivalTimeOfPacket
                        self.lastSequence = currFrameNbr
            except:
                # Stop listening upon requesting PAUSE or TEARDOWN
                if self.playEvent.isSet():
                    self.displayStats()
                    break

                # Upon receiving ACK for TEARDOWN request,
                # close the RTP socket
                if self.teardownAcked == 1:
                    self.displayStats()
                    self.checkSocketIsOpen = False
                    try:
                        self.rtpSocket.shutdown(socket.SHUT_RDWR)
                        self.rtpSocket.close()
                    except:
                        pass
                    break

    def writeFrame(self, data):
        """Write the received frame to a temp image file. Return the image file."""
        cachename = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
        file = open(cachename, "wb")
        file.write(data)
        file.close()
        return cachename

    def updateMovie(self, imageFile):
        """Update the image file as video frame in the GUI."""
        photo = ImageTk.PhotoImage(Image.open(imageFile))
        self.label.configure(image=photo, height=288)
        self.label.image = photo

    def connectToServer(self):
        """Connect to the Server. Start a new RTSP/TCP session."""
        self.checkSocketIsOpen = True
        self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.rtspSocket.connect((self.serverAddr, self.serverPort))
        except:
            tkinter.messagebox.showwarning('Connection Failed', 'Connection to \'%s\' failed.' % self.serverAddr)

    def sendRtspRequest(self, requestCode):
        """Send RTSP request to the server."""
        # -------------
        # TO COMPLETE
        # -------------
        # Setup request
        if requestCode == self.SETUP:  # and self.state == self.INIT:
            threading.Thread(target=self.recvRtspReply).start()
            # Update RTSP sequence number.
            # ...
            self.rtspSeq = self.rtspSeq + 1
            # Write the RTSP request to be sent.
            # request = ...
            request = "SETUP %s RTSP/1.0\nCSeq: %d\nTRANSPORT: RTP/UDP; Client_port= %d" % (self.fileName, self.rtspSeq, self.rtpPort)

            # Keep track of the sent request.
            # self.requestSent = ...
            self.requestSent = self.SETUP
        # Play request
        elif requestCode == self.PLAY:  # and self.state == self.READY:
            # Update RTSP sequence number.
            # ...
            self.rtspSeq = self.rtspSeq + 1
            # Write the RTSP request to be sent.
            # request = ...
            request = "PLAY %s RTSP/1.0\nCSeq: %d\nSESSION: %d" % (self.fileName, self.rtspSeq, self.sessionId)
            # Keep track of the sent request.
            # self.requestSent = ...
            self.requestSent = self.PLAY
        # Pause request
        elif requestCode == self.PAUSE:  # and self.state == self.PLAYING:
            # Update RTSP sequence number.
            # ...
            self.rtspSeq = self.rtspSeq + 1
            # Write the RTSP request to be sent.
            # request = ...
            request = "PAUSE %s RTSP/1.0\nCSeq: %d\nSESSION: %d" % (self.fileName, self.rtspSeq, self.sessionId)
            # Keep track of the sent request.
            # self.requestSent = ...
            self.requestSent = self.PAUSE
        # Teardown request
        elif requestCode == self.TEARDOWN:  # and not self.state == self.INIT:
            # Update RTSP sequence number.
            # ...
            self.rtspSeq = self.rtspSeq + 1
            # Write the RTSP request to be sent.
            # request = ...
            request = "TEARDOWN %s RTSP/1.0\nCSeq: %d\nSESSION: %d" % (self.fileName, self.rtspSeq, self.sessionId)

            # Keep track of the sent request.
            # self.requestSent = ...
            self.requestSent = self.TEARDOWN
        elif requestCode == self.DESCRIBE:
            self.rtspSeq = self.rtspSeq + 1
            request = "DESCRIBE %s RTSP/1.0\nCSeq: %d\nSESSION: %d" % (self.fileName, self.rtspSeq, self.sessionId)
            self.requestSent = self.DESCRIBE

        elif requestCode == self.FORWARD:
            # Update RTSP sequence number.
            # ...
            self.rtspSeq = self.rtspSeq + 1
            # Write the RTSP request to be sent.
            # request = ...
            request = "FORWARD %s RTSP/1.0\nCSeq: %d\nSESSION: %d" % (self.fileName, self.rtspSeq, self.sessionId)
            # Keep track of the sent request.
            # self.requestSent = ...
            self.requestSent = self.FORWARD

        elif requestCode == self.PREV:
            # Update RTSP sequence number.
            # ...
            if self.rtspSeq <= 50:
                self.rtspSeq = 0
            else:
                self.rtspSeq = self.rtspSeq - 50
            # Write the RTSP request to be sent.
            # request = ...
            request = "PREVIOUS %s RTSP/1.0\nCSeq: %d\nSESSION: %d" % (self.fileName, self.rtspSeq, self.sessionId)
            # Keep track of the sent request.
            # self.requestSent = ...
            self.requestSent = self.PREV

        else:
            return

        # Send the RTSP request using rtspSocket.
        # ...
        self.rtspSocket.send(request.encode())
        print('\nDu lieu gui:\n' + request)

    def recvRtspReply(self):
        """Receive RTSP reply from the server."""
        while True:
            reply = self.rtspSocket.recv(1024)

            if reply:
                self.parseRtspReply(reply.decode("utf-8"))

            # Close the RTSP socket upon requesting Teardown
            if self.requestSent == self.TEARDOWN:
                self.rtspSocket.shutdown(socket.SHUT_RDWR)
                self.rtspSocket.close()
                break

    def parseRtspReply(self, data):
        """Parse the RTSP reply from the server."""
        lines = data.split('\n')
        seqNum = int(lines[1].split(' ')[1])

        # Process only if the server reply's sequence number is the same as the request's
        if seqNum == self.rtspSeq:
            session = int(lines[2].split(' ')[1])
            # New RTSP session ID
            if self.sessionId == 0:
                self.sessionId = session

            # Process only if the session ID is the same
            if self.sessionId == session:
                if int(lines[0].split(' ')[1]) == 200:
                    if self.requestSent == self.SETUP:
                        # -------------
                        # TO COMPLETE
                        # -------------
                        # Update RTSP state.
                        # self.state = ...
                        self.totalTime = float(lines[3].split(' ')[1])
                        self.state = self.READY
                        # Open RTP port.
                        self.openRtpPort()
                    elif self.requestSent == self.PLAY:
                        # self.state = ...
                        self.state = self.PLAYING
                        # start timer if not already playing
                        if self.timerBegin == 0:
                            self.timerBegin = time.perf_counter()
                            self.arrivalTimeofPreviousPacket = time.perf_counter()
                    elif self.requestSent == self.PAUSE:
                        # self.state = ...
                        self.state = self.READY

                        # set timer when paused and playing previously
                        if self.timerBegin > 0:
                            self.timerEnd = time.perf_counter()
                            self.timer += self.timerEnd - self.timerBegin
                            self.timerBegin = 0
                        # The play thread exits. A new thread is created on resume.
                        self.playEvent.set()
                    elif self.requestSent == self.TEARDOWN:
                        # self.state = ...
                        self.state = self.INIT
                        self.timerEnd = time.perf_counter()
                        # end timer
                        self.timer += self.timerEnd - self.timerBegin
                        # Flag the teardownAcked to close the socket.
                        self.teardownAcked = 1

                    elif self.requestSent == self.DESCRIBE:
                        # self.state = ...
                        self.displayDescription(lines)

    def openRtpPort(self):
        """Open RTP socket binded to a specified port."""
        # -------------
        # TO COMPLETE
        # -------------
        # Create a new datagram socket to receive RTP packets from the server
        # self.rtpSocket = ...
        self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Set the timeout value of the socket to 0.5sec
        # ...
        self.rtpSocket.settimeout(0.5)
        try:
            # Bind the socket to the address using the RTP port given by the client user
            # ...
            self.state = self.READY
            self.rtpSocket.bind(('', self.rtpPort))
        except:
            tkinter.messagebox.showwarning('Unable to Bind', 'Unable to bind PORT=%d' % self.rtpPort)

    def handler(self):  # khi bấm vào dấu X
        """Handler on explicitly closing the GUI window."""
        self.pauseMovie()
        if tkinter.messagebox.askokcancel("Quit?", "Are you sure you want to quit?"):
            self.sendRtspRequest(self.TEARDOWN)
            if (self.checkSocketIsOpen and self.state != self.INIT):
                self.rtpSocket.shutdown(socket.SHUT_RDWR)
                self.rtpSocket.close()
            self.master.destroy()  # Close the gui window
            sys.exit(0)


    def displayDescription(self, lines):
        top = Toplevel()
        top.title("Description")
        top.geometry('300x180')
        Lb1 = Listbox(top, width=50, height=30)
        Lb1.insert(1, "Describe: ")
        Lb1.insert(2, "Name Video: " + str(self.fileName))
        Lb1.insert(3, lines[1])
        Lb1.insert(4, lines[2])
        Lb1.insert(5, lines[3])
        Lb1.insert(6, lines[4])
        Lb1.insert(7, lines[5])
        Lb1.insert(8, lines[6])
        Lb1.insert(9, lines[7])
        Lb1.insert(10, lines[8])
        Lb1.insert(11, "Thoi diem trong video: " + "%02d:%02d" % (self.currentTime // 60, self.currentTime % 60))
        Lb1.pack()

    def displayStats(self):
        """Displays observed statistics"""
        totalPackets = ((self.counter) / (self.countTotalPacket)) * 100

        top1 = Toplevel()
        top1.title("Statistics")
        top1.geometry('300x170')
        Lb2 = Listbox(top1, width=80, height=20)
        Lb2.insert(1, "Current Packets No.%d " % self.frameNbr)
        Lb2.insert(2, "Total Streaming Packets: %d packets" % self.countTotalPacket)
        Lb2.insert(3, "Packets Received: %d packets" % self.packets)
        Lb2.insert(4, "Packets Lost: %d packets" % self.counter)
        Lb2.insert(5, "Packet Loss Rate: %d%%" % totalPackets)
        Lb2.insert(6, "Play time: %.2f seconds" % self.timer)
        Lb2.insert(7, "Bytes received: %d bytes" % self.bytes)
        Lb2.insert(8, "Video Data Rate: %d bytes per second" % (self.bytes / self.timer))
        Lb2.insert(9, "Total Jitter: %.3fms" % (self.totalJitter * 1000))
        Lb2.insert(10, "Average Jitter: %.3fms" % ((self.totalJitter / self.packets ) * 1000))
        Lb2.pack()
        # top1.mainloop()


