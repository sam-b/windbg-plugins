import pykd

return_reg = "rax"
stack_pointer = "rsp"

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
			disas = pykd.dbgCommand("uf ntdll!RtlAllocateHeap").split('\n')
			for i in disas:
				if 'ret' in i:
					self.ret_addr = i.split()[0]
					break
			self.bp_end = pykd.setBp(int(self.ret_addr, 16), self.return_call_back)
		return False
	
	def return_call_back(self,bp):
		self.out += hex(pykd.reg(return_reg))
		print self.out
		return False
		
try:
	pykd.reg("rax")
except:
	return_reg = "eax"
	stack_pointer = "esp"

handle_allocate_heap()
pykd.go()