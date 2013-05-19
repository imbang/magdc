import os
import optparse

from twisted.internet import reactor, protocol
from twisted.protocols import basic

from common import COMMANDS, display_message, validate_file_md5_hash, get_file_md5_hash, read_bytes_from_file, clean_and_split_input

class MagSrvProtocol(basic.LineReceiver):
	delimiter = '\n'

	def getAuth(self):
                return True

	def connectionMade(self):
		self.factory.clients.append(self)
		self.file_handler = None
		self.file_data = ()
                self.user = None
                self.passwd = None
                self.host = self.transport.getPeer().host
                self.staid = None
                self.isLogin = False

		self.transport.write('Welcome to MAGNETICS DATA CENTER(v1.0)\n')
		self.transport.write('auth\n')
		
		display_message('Connection from: %s (%d clients total)' % (self.host, len(self.factory.clients)))
		
	def connectionLost(self, reason):
		self.factory.clients.remove(self)
		self.file_handler = None
		self.file_data = ()
		
		display_message('Connection from %s lost (%d clients left)' % (self.host, len(self.factory.clients)))
            
	def lineReceived(self, line):
		display_message('Received the following line from the client [%s]: %s' % (self.host, line))
		
		data = self._cleanAndSplitInput(line)
		if len(data) == 0 or data == '':
			return 
		
		command = data[0].lower()
		if not command in COMMANDS:
                        self.transport.write('%s\n' % (command))
			self.transport.write('Invalid command\n')
			return
		    
		if command == 'list':
                        pass

		elif command == 'auth':
                        self.isLogin = self.getAuth()
                        if self.isLogin:
                                self.transport.write('file\n')
                                
                        return

		elif command == 'put':
			try:
				filename = data[1]
				file_hash = data[2]
			except IndexError:
				self.transport.write('Missing filename or file MD5 hash\n')
				return

			self.file_data = (filename, file_hash)
			
			# Switch to the raw mode (for receiving binary data)
			display_message('Receiving file: %s' % (filename))
			self.setRawMode()
		elif command == 'help':
			self.transport.write('Available commands:\n\n')
			
			for key, value in COMMANDS.iteritems():
				self.transport.write('%s - %s\n' % (value[0], value[1]))
							
		elif command == 'quit':
			self.transport.loseConnection()
			
	def rawDataReceived(self, data):
		filename = self.file_data[0]
		file_path = os.path.join(self.factory.files_path, filename)
		
		display_message('Receiving file chunk (%d KB)' % (len(data)))
		
		if not self.file_handler:
			self.file_handler = open(file_path, 'wb')
		
		if data.endswith('\r\n'):
			# Last chunk
			data = data[:-2]
			self.file_handler.write(data)
			self.setLineMode()
			
			self.file_handler.close()
			self.file_handler = None
			self.transport.loseConnection()
			
			if validate_file_md5_hash(file_path, self.file_data[1]):
				self.transport.write('put-ok\n')
				display_message('File %s has been successfully transfered' % (filename))
			else:
				os.unlink(file_path)
				self.transport.write('put-fail\n')
				display_message('File %s has been successfully transfered, but deleted due to invalid MD5 hash' % (filename))
		else:
			self.file_handler.write(data)
		
	def _send_list_of_files(self):
		files = self._get_file_list()
		self.factory.files = files
		
		self.transport.write('Files (%d): \n\n' % len(files))	
		for key, value in files.iteritems():
			self.transport.write('- %s (%d.2 KB)\n' % (key, (value[1] / 1024.0)))
			
			
	def _get_file_list(self):
		""" Returns a list of the files in the specified directory as a dictionary:
		
		dict['file name'] = (file path, file size, file md5 hash)
		"""
		
		file_list = {}
		for filename in os.listdir(self.factory.files_path):
			file_path = os.path.join(self.factory.files_path, filename)
			
			if os.path.isdir(file_path):
				continue
			
			file_size = os.path.getsize(file_path)
			md5_hash = get_file_md5_hash(file_path)

			file_list[filename] = (file_path, file_size, md5_hash)

		return file_list
			
	def _cleanAndSplitInput(self, input):
		input = input.strip()
		input = input.split(' ')
		
		return input

class MagSrvFactory(protocol.ServerFactory):
	
	protocol = MagSrvProtocol
	
	def __init__(self, files_path):
		self.files_path = files_path
		
		self.clients = []
		self.files = None
	
if __name__ == '__main__':
	parser = optparse.OptionParser()
	parser.add_option('-p', '--port', action = 'store', type = 'int', dest = 'port', default = 1234, help = 'server listening port')
	parser.add_option('--path', action = 'store', type = 'string', dest = 'path', help = 'directory where the incoming files are saved')
	(options, args) = parser.parse_args()
	
	display_message('Listening on port %d, serving files from directory: %s' % (options.port, options.path))

	reactor.listenTCP(options.port, MagSrvFactory(options.path))
	reactor.run()
