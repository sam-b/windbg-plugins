import pykd

return_reg = "rax"

def get_address(localAddr):
	res = pykd.dbgCommand("x " + localAddr)
	result_count = res.count("\n")
	if result_count == 0:
		print localAddr + " not found."
		return None
	if result_count > 1:
		print "[-] Warning, more than one result for", localAddr	
	return res.split()[0]
	
class handle_allocate_heap(pykd.eventHandler):
	def __init__(self):
		addr = get_address("ntdll!RtlAllocateHeap")
		if addr == None:
			return
		self.bp_init = pykd.setBp(int(addr, 16), self.enter_call_back)
		self.bp_end = None
		
	def enter_call_back(self,bp):
		print "RtlAllocateHeap called with: " 
		print pykd.dbgCommand("kv")
		if self.bp_end == None:
			self.ret_addr = pykd.dbgCommand("dd esp L1").split()[1]
			self.bp_end = pykd.setBp(int(self.ret_addr, 16), self.return_call_back)
		return False
	
	def return_call_back(self,bp):
		print "RtlAllocateHeap Returned: " + str(pykd.reg(return_reg))
		return False
		
class handle_reallocate_heap(pykd.eventHandler):
	def __init__(self):
		addr = get_address("ntdll!RtlReAllocateHeap")
		if addr == None:
			return
		self.bp_init = pykd.setBp(int(addr, 16), self.enter_call_back)
		self.bp_end = None
		
	def enter_call_back(self,bp):
		print "RtlReAllocateHeap"
		print pykd.dbgCommand("kv")
		if self.bp_end == None:
			self.ret_addr = pykd.dbgCommand("dd esp L1").split()[1]
			self.bp_end = pykd.setBp(int(self.ret_addr, 16), self.return_call_back)
		return False

	def return_call_back(self,bp):
		print "RtlReallocateHeap Returned: " + str(pykd.reg(return_reg))
		return False
		
class handle_virtual_alloc(pykd.eventHandler):
	def __init__(self):
		addr = get_address("Kernel32!VirtualAlloc")
		if addr == None:
			return
		self.bp_init = pykd.setBp(int(addr, 16), self.call_back)
		self.bp_end = None
		
	def call_back(self,bp):
		print "VirtualAlloc called with "
		print pykd.dbgCommand("kv")
		if self.bp_end == None:
			self.ret_addr = pykd.dbgCommand("dd esp L1").split()[1]

			print "[+] saving return ptr: " + self.ret_addr
			self.bp_end = pykd.setBp(int(self.ret_addr, 16), self.return_call_back)
		return False

	def return_call_back(self,bp):
		print "VirtualAlloc returned " + str(pykd.reg(return_reg))
		return False

class handle_free_heap(pykd.eventHandler):
	def __init__(self):
		addr = get_address("ntdll!RtlFreeHeap")
		if addr == None:
			return
		self.bp_init = pykd.setBp(int(addr, 16), self.enter_call_back)
		self.bp_end = None
		
	def enter_call_back(self,bp):
		print "RtlFreeHeap called with "
		print pykd.dbgCommand("kv")
		if self.bp_end == None:
			self.ret_addr = pykd.dbgCommand("dd esp L1").split()[1]
			self.bp_end = pykd.setBp(int(self.ret_addr, 16), self.return_call_back)
		return False
		
	def return_call_back(self,bp):
		print "RtlFreeHeap returned: " + str(pykd.reg(return_reg))
		return False

try:
	pykd.reg("rax")
except:
	return_reg = "eax"

handle_allocate_heap()
handle_reallocate_heap()
handle_virtual_alloc()
handle_free_heap()
pykd.go()