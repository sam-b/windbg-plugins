import pykd
from os.path import expanduser
import timeit

start = timeit.default_timer()

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
	
class time(pykd.eventHandler):
	def __init__(self):
		addr = get_address("jscript9!StrToDbl")
		if addr == None:
			return
		self.start = timeit.default_timer()
		self.bp_init = pykd.setBp(int(addr, 16), self.enter_call_back)
	def enter_call_back(self,bp):
		end = timeit.default_timer()
		print "Heap spray took: " + str(end - self.start)
		return True

time()
pykd.go()