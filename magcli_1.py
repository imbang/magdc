from twisted.internet import reactor, protocol
from twisted.protocols import basic
import os
import optparse
from common import read_bytes_from_file


# a client protocol

class MagClient(basic.LineReceiver):
    """Once connected, send a message, then print the result."""
      
    def connectionMade(self):
##        self.transport.write("hello, world!")
        print "trying to connect..."
##        command="hello"
##        self.transport.write('%s\n' % (command))
##        self.setLineMode()
    
    def dataReceived(self, data):
        "As soon as any data is received, write it back."
##        data = self._cleanAndSplitInput(data)
##        if data is None:
##            return
        
        if data is None or len(data) == 0 or data == '':
	    return
        data = data.strip()
##        if data=='.':
##            print '.'
##            return
        
##        print data
        if data.endswith('auth'):
            dt = data.split('\n')
            dt = dt[0].split(' ')
            print '%s %s %s %s %s' % (dt[0],dt[1],dt[2],dt[3],dt[4])
            print "sending authentification..."
            self.transport.write('auth %s %s %s %d\n' % (self.factory.user,self.factory.psw,self.factory.ipaddr,self.factory.staid))
        elif data.endswith('file'):
            try:
                file_path = self.factory.filename
                filename = self.factory.filename
            except IndexError:
                print 'Missing local file path or remote file name'
                return
            
            if not os.path.isfile(file_path):
                print 'This file does not exist'
                return

            file_size = os.path.getsize(file_path) / 1024
            
            print 'Uploading file: %s (%d KB)' % (filename, file_size)
            
            self.transport.write('PUT %s %s\n' % (os.path.basename(filename), file_path))
            self.setRawMode()
            
            for bytes in read_bytes_from_file(file_path):
                self.transport.write(bytes)
            
            self.transport.write('\r\n')   
            
            # When the transfer is finished, we go back to the line mode 
            self.setLineMode()
##        else:
##            self.transport.write('%s %s\n' % (command, data[1]))

##        self.factory.deferred.addCallback(self._display_response)
##        self.transport.loseConnection()

    def LineReceived(self, line):
        "As soon as any data is received, write it back."
        print "Server said:", line
        #self.transport.loseConnection()
        
    def connectionLost(self, reason):
        print "connection lost"

    def _cleanAndSplitInput(self, input):
	input = input.strip()
	input = input.split(' ')
	return input

class MagFactory(protocol.ClientFactory):
    protocol = MagClient

    def __init__(self, user,psw,ipaddr,staid,filename):
        self.filename = filename
        self.user = user
        self.psw = psw
        self.ipaddr = ipaddr
        self.staid = staid

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed - goodbye!"
        reactor.stop()
    
    def clientConnectionLost(self, connector, reason):
        print "Connection lost - goodbye!"
        reactor.stop()


# this connects the protocol to a server runing on port 8000
def main(ip,port,filename):
    fname = filename
    user='imbang'
    psw='laksono'
    ipaddr='172.30.91.125'
    staid=1
    f = MagFactory(user,psw,ipaddr,staid,filename)
    reactor.connectTCP(ip, port, f)
    reactor.run()

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('--ip', action = 'store', type = 'string', dest = 'ip_address', default = '127.0.0.1', help = 'server IP address')
    parser.add_option('-p', '--port', action = 'store', type = 'int', dest = 'port', default = 8000, help = 'server port')
    parser.add_option('--file', action = 'store', type = 'string', dest = 'filename', help = 'File will be uploaded')
    
    (options, args) = parser.parse_args()

##    print 'Client started...'
    main(options.ip_address,options.port,options.filename)
