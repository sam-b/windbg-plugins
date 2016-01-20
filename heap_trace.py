import pykd

def get_address(localAddr):
	res = pykd.dbgCommand("x " + localAddr)
	if res.count("\n") > 1:
		print "[-] Warning, more than one result for", localAddr
	return res.split()[0]
	
class handle_allocate_heap(pykd.eventHandler):
	def __init__(self):
		addr = get_address("ntdll!RtlAllocateHeap")
		self.bp_init = pykd.setBp(int(addr, 16), self.call_back)
		self.bp_end = None
		pykd.go()
		
	def call_back(self,args):
		print "RtlAllocateHeap"
		return False
		
class handle_reallocate_heap(pykd.eventHandler):
	def __init__(self):
		addr = get_address("ntdll!RtlReAllocateHeap")
		self.bp_init = pykd.setBp(int(addr, 16), self.call_back)
		self.bp_end = None
		pykd.go()
		
	def call_back(self,args):
		print "RtlReAllocateHeap"
		return False
		
class handle_virtual_alloc(pykd.eventHandler):
	def __init__(self):
		addr = get_address("Kernel32!VirtualAlloc")
		self.bp_init = pykd.setBp(int(addr, 16), self.call_back)
		self.bp_end = None
		pykd.go()
		
	def call_back(self,args):
		print "VirtualAlloc"
		return False

class handle_free_heap(pykd.eventHandler):
	def __init__(self):
		addr = get_address("ntdll!RtlFreeHeap")
		self.bp_init = pykd.setBp(int(addr, 16), self.call_back)
		self.bp_end = None
		pykd.go()
		
	def call_back(self,args):
		print "RtlFreeHeap"
		return False
		
handle_allocate_heap()
handle_reallocate_heap()
handle_virtual_alloc()
handle_free_heap()