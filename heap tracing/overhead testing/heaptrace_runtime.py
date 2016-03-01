import pykd
from os.path import expanduser
import timeit

home = expanduser("~")
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
	
class start(pykd.eventHandler):
	def __init__(self):
		addr = get_address("jscript9!StrToDbl")
		if addr == None:
			return
		self.start = timeit.default_timer()
		handle_allocate_heap()
		handle_free_heap()
		handle_realloc_heap()
		self.bp_init = pykd.setBp(int(addr, 16), self.enter_call_back)

	def enter_call_back(self,bp):
		end = timeit.default_timer()
		print "Heap spray took: " + str(end - self.start)
		return True
		
	
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
		if arch_bits == 32:
			esp = pykd.reg(stack_pointer)
			self.out += hex(pykd.ptrPtr(esp + 4)) + " , "
			self.out += hex(pykd.ptrMWord(esp + 0x8)) + " , "
			self.out += hex(pykd.ptrMWord(esp + 0xC)) + ") = "
		else:
			self.out += hex(pykd.reg("rcx")) + " , "
			self.out += hex(pykd.reg("rdx")) + " , " 
			self.out += hex(pykd.reg("r8")) +  ") = "
		if self.bp_end == None:
			disas = pykd.dbgCommand("uf ntdll!RtlAllocateHeap").split('\n')
			for i in disas:
				if 'ret' in i:
					self.ret_addr = i.split()[0]
					break
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
		if arch_bits == 32:
			esp = pykd.reg(stack_pointer)
			self.out += hex(pykd.ptrPtr(esp + 4)) + " , "
			self.out += hex(pykd.ptrMWord(esp + 0x8)) + " , "
			self.out += hex(pykd.ptrPtr(esp + 0xC)) + ") = "
		else:
			self.out += hex(pykd.reg("rcx")) + " , "
			self.out += hex(pykd.reg("rdx")) + " , "
			self.out += hex(pykd.reg("r8")) + ") = "
		if self.bp_end == None:
			disas = pykd.dbgCommand("uf ntdll!RtlFreeHeap").split('\n')
			for i in disas:
				if 'ret' in i:
					self.ret_addr = i.split()[0]
					break
			self.bp_end = pykd.setBp(int(self.ret_addr, 16), self.return_call_back)
		return False
		
	def return_call_back(self,bp):
		#returns a BOOLEAN which is a byte under the hood
		ret_val = hex(pykd.reg("al"))
		log.write(self.out + ret_val + "\n")
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
		if arch_bits == 32:
			esp = pykd.reg(stack_pointer)
			self.out += hex(pykd.ptrPtr(esp + 4)) + " , "
			self.out += hex(pykd.ptrMWord(esp + 0x8)) + " , " 
			self.out += hex(pykd.ptrPtr(esp + 0xC)) + " , " 
			self.out += hex(pykd.ptrMWord(esp + 0x10)) + ") = "
		else:
			self.out += hex(pykd.reg("rcx")) + " , "
			self.out += hex(pykd.reg("rdx")) + " , " 
			self.out += hex(pykd.reg("r8")) + " , " 
			self.out += hex(pykd.reg("r9")) + ") = "
		if self.bp_end == None:
			disas = pykd.dbgCommand("uf ntdll!RtlReAllocateHeap").split('\n')
			for i in disas:
				if 'ret' in i:
					self.ret_addr = i.split()[0]
					break
			self.bp_end = pykd.setBp(int(self.ret_addr, 16), self.return_call_back)
		return False
		
	def return_call_back(self,bp):
		log.write(self.out + hex(pykd.reg(return_reg)) + "\n")
		return False

log = open(home + "\log.log","w+")
		
try:
	pykd.reg("rax")
except:
	arch_bits = 32
	return_reg = "eax"
	stack_pointer = "esp"

start()
pykd.go()