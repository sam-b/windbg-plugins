import pykd

return_reg = "rax"
stack_pointer = "rsp"
arch_bits = 64
log = None
def get_address(localAddr):
	res = pykd.dbgCommand("x " + localAddr)
	result_count = res.count("\n")
	if result_count == 0:
		print localAddr + " not found."
		return None
	if result_count > 1:
		print "[-] Warning, more than one result for", localAddr	
	return res.split()[0]
	
	
#RtlAllocateHeap(
# IN PVOID                HeapHandle,
# IN ULONG                Flags,
# IN ULONG                Size );
class handle_allocate_heap(pykd.eventHandler):
	def __init__(self):
		addr = get_address("ntdll!RtlAllocateHeap")
		if addr == None:
			return
		self.bp_init = pykd.setBp(int(addr, 16), self.enter_call_back)
		self.bp_end = None
		
	def enter_call_back(self,bp):
		self.out = "RtlAllocateHeap(" 
		esp = pykd.reg("esp")
		self.out += hex(pykd.ptrPtr(esp + 4)) + " , "
		self.out += hex(pykd.ptrMWord(esp + 0x8)) + " , "
		self.out += hex(pykd.ptrMWord(esp + 0xC)) + ") = "
		if self.bp_end == None:
			self.ret_addr = pykd.dbgCommand("dd esp L1").split()[1]
			self.bp_end = pykd.setBp(int(self.ret_addr, 16), self.return_call_back)
		return False
	
	def return_call_back(self,bp):
		log.write(self.out + hex(pykd.reg(return_reg)) + "\n")
		return False

#RtlFreeHeap(
#IN PVOID                HeapHandle,
#IN ULONG                Flags OPTIONAL,
#IN PVOID                MemoryPointer );
class handle_free_heap(pykd.eventHandler):
	def __init__(self):
		addr = get_address("ntdll!RtlFreeHeap")
		if addr == None:
			return
		self.bp_init = pykd.setBp(int(addr, 16), self.enter_call_back)
		self.bp_end = None
		
	def enter_call_back(self,bp):
		self.out = "RtlFreeHeap("
		esp = pykd.reg("esp")
		self.out += hex(pykd.ptrPtr(esp + 4)) + " , "
		self.out += hex(pykd.ptrMWord(esp + 0x8)) + " , "
		self.out += hex(pykd.ptrPtr(esp + 0xC)) + ") = "
		if self.bp_end == None:
			self.ret_addr = pykd.dbgCommand("dd esp L1").split()[1]
			self.bp_end = pykd.setBp(int(self.ret_addr, 16), self.return_call_back)
		return False
		
	def return_call_back(self,bp):
		log.write(self.out + hex(pykd.reg(return_reg)) + "\n")
		return False

#RtlReAllocateHeap(
#IN PVOID                HeapHandle,
#IN ULONG                Flags,
# IN PVOID                MemoryPointer,
# IN ULONG                Size );
		
class handle_realloc_heap(pykd.eventHandler):
	def __init__(self):
		addr = get_address("ntdll!RtlReAllocateHeap")
		if addr == None:
			return
		self.bp_init = pykd.setBp(int(addr, 16), self.enter_call_back)
		self.bp_end = None
		
	def enter_call_back(self,bp):
		self.out = "RtlReAllocateHeap("
		esp = pykd.reg("esp")
		self.out += hex(pykd.ptrPtr(esp + 4)) + " , "
		self.out += hex(pykd.ptrMWord(esp + 0x8)) + " , " 
		self.out += hex(pykd.ptrPtr(esp + 0xC)) + " , " 
		self.out += hex(pykd.ptrMWord(esp + 0x10)) + ") = "
		if self.bp_end == None:
			self.ret_addr = pykd.dbgCommand("dd esp L1").split()[1]
			self.bp_end = pykd.setBp(int(self.ret_addr, 16), self.return_call_back)
		return False
		
	def return_call_back(self,bp):
		log.write(self.out + hex(pykd.reg(return_reg)) + "\n")
		return False

log = open("C:\Users\sam\Desktop\log.log","w+")
		
try:
	pykd.reg("rax")
except:
	arch_bits = 32
	return_reg = "eax"
	stack_pointer = "esp"

handle_allocate_heap()
handle_free_heap()
handle_realloc_heap()
pykd.go()