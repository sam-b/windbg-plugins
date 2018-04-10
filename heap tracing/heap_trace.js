/*
	Uses windbg's JavaScript scripting support to trace user mode memory allocations in a format viewable with villoc
	Heavily based off of https://doar-e.github.io/blog/2017/12/01/debugger-data-model/
*/

"use strict";

var archBits = 0;
var returnReg = null;
var stackPointer = null;
var allocateHeapOut = null;
var reallocateHeapOut = null;
var freeHeapOut = null;

function hex(val) {
	return val.toString(16);
}

function print(msg) {
	host.diagnostics.debugLog(msg);
}

function findRetAddrs(mod, name){
	var addrs = [];
	for(var line of host.namespace.Debugger.Utility.Control.ExecuteCommand("uf " + mod + ':' + name)){
		if(line.includes('ret')){
			var addr = host.parseInt64(line.split(" ")[0], 16);
			addrs.push(addr);
		}
	}
	return addrs;
}
/*#RtlAllocateHeap(
# IN PVOID                HeapHandle,
# IN ULONG                Flags,
# IN ULONG                Size );*/
function handleAllocateHeap() {
	var regs = host.currentThread.Registers.User;
	var out = "RtlAllocateHeap(";
	var args = null;
	if(archBits == 32){
		args = host.memory.readMemoryValues(regs[stackPointer] + 4, 3, 4);
	} else {
		args = [regs.rcx, regs.rdx, regs.r8];
	}
	out += hex(args[0]) + ", ";
	out += hex(args[1]) + ", ";
	out += hex(args[2]) + ") = ";
	allocateHeapOut = out;
	return false;
}

/* #RtlReAllocateHeap(
#IN PVOID                HeapHandle,
#IN ULONG                Flags,
# IN PVOID                MemoryPointer,
# IN ULONG                Size );
*/
function handleReAllocateHeap() {
	var regs = host.currentThread.Registers.User;
	var out = "RtlReAllocateHeap(";
	var args = null;
	if(archBits == 32){
		args = host.memory.readMemoryValues(regs[stackPointer] + 4, 4, 4);
	} else {
		args = [regs.rcx, regs.rdx, regs.r8, regs.r9];
	}
	out += hex(args[0]) + ", ";
	out += hex(args[1]) + ", ";
	out += hex(args[2]) + ", ";
	out += hex(args[3]) + ") = ";
	reallocateHeapOut = out;
	return false;
}

/*#RtlFreeHeap(
#IN PVOID                HeapHandle,
#IN ULONG                Flags OPTIONAL,
#IN PVOID                MemoryPointer );*/
function handleFreeHeap() {
	var regs = host.currentThread.Registers.User;
	var out = "RtlFreeHeap(";
	var args = null;
	if(archBits == 32){
		args = host.memory.readMemoryValues(regs[stackPointer] + 4, 3, 4);
	} else {
		args = [regs.rcx, regs.rdx, regs.r8];
	}
	out += hex(args[0]) + ", ";
	out += hex(args[1]) + ", ";
	out += hex(args[2]) + ") = ";
	freeHeapOut = out;
	return false;
}

function handleAllocateHeapRet() {
	var regs = host.currentThread.Registers.User;
	if(allocateHeapOut != null){
		print(allocateHeapOut + hex(regs[returnReg]) + "\r\n");
		allocateHeapOut = null;
	}
	return false;
}

function handleReAllocateHeapRet() {
	var regs = host.currentThread.Registers.User;
	if(reallocateHeapOut != null){
		print(reallocateHeapOut + hex(regs[returnReg]) + "\r\n");
		reallocateHeapOut = null;
	}
	return false;
}

function handleFreeHeapRet() {
	var regs = host.currentThread.Registers.User;
	if(freeHeapOut != null){
		print(freeHeapOut + hex(regs[returnReg]) + "\r\n");
		freeHeapOut = null;
	}
	return false;
}

function invokeScript() {
	try {
		host.currentThread.Registers.User.rax;
		archBits = 64;
		returnReg = "rax";
		stackPointer = "rsp";
	} catch (e) {
		archBits = 32;
		returnRed = "eax";
		stackPointer = "esp";
	}

	print("Running on a " + archBits + "-bit process.\r\n");

	var RtlAllocateHeap = host.getModuleSymbolAddress('ntdll', 'RtlAllocateHeap');
	var RtlFreeHeap = host.getModuleSymbolAddress('ntdll', 'RtlFreeHeap');
	var RtlReAllocateHeap = host.getModuleSymbolAddress('ntdll', 'RtlReAllocateHeap');

	print('Hooking:\r\n\tRltAllocateHeap: ' + hex(RtlAllocateHeap) + "\r\n\tRtlFreeHeap: " + hex(RtlFreeHeap) + "\r\n\tRtlReAllocateHeap: " + hex(RtlReAllocateHeap) + "\r\n");
	var breakpointsAlreadySet = host.currentProcess.Debug.Breakpoints.Any(
        bp => bp.Address == RtlAllocateHeap || bp.Address == RtlFreeHeap || by.Address == RtlReAllocateHeap
    );
	if(breakpointsAlreadySet == false) {
		host.namespace.Debugger.Utility.Control.ExecuteCommand('bp /w "@$scriptContents.handleAllocateHeap()" ' + RtlAllocateHeap.toString(16));
		host.namespace.Debugger.Utility.Control.ExecuteCommand('bp /w "@$scriptContents.handleFreeHeap()" ' + RtlFreeHeap.toString(16));
		host.namespace.Debugger.Utility.Control.ExecuteCommand('bp /w "@$scriptContents.handleReAllocateHeap()" ' + RtlReAllocateHeap.toString(16));
	}
	var RtlAllocateHeapRet = findRetAddrs("ntdll", "RtlAllocateHeap");
	var RtlFreeHeapRet = findRetAddrs('ntdll', 'RtlFreeHeap');
	var RtlReAllocateHeapRet = findRetAddrs('ntdll', 'RtlReAllocateHeap');

	print('\tRltAllocateHeapRet: ' + hex(RtlAllocateHeapRet) + "\r\n\tRtlFreeHeapRet: " + hex(RtlFreeHeapRet) + "\r\n\tRtlReAllocateHeapRet: " + hex(RtlReAllocateHeapRet) + "\r\n");

	var retBreakpointsAlreadySet = host.currentProcess.Debug.Breakpoints.Any(
        bp => bp.Address in RtlAllocateHeapRet || bp.Address in RtlFreeHeapRet || bp.Address in RtlReAllocateHeapRet
    );

	if(retBreakpointsAlreadySet == false) {
		for(var addr in RtlAllocateHeapRet){
			host.namespace.Debugger.Utility.Control.ExecuteCommand('bp /w "@$scriptContents.handleAllocateHeapRet()" ' + RtlAllocateHeapRet[addr].toString(16));
		}
		for(var addr in RtlFreeHeapRet){
			host.namespace.Debugger.Utility.Control.ExecuteCommand('bp /w "@$scriptContents.handleFreeHeapRet()" ' + RtlFreeHeapRet[addr].toString(16));
		}
		for(var addr in RtlReAllocateHeapRet){
			host.namespace.Debugger.Utility.Control.ExecuteCommand('bp /w "@$scriptContents.handleReAllocateHeapRet()" ' + RtlReAllocateHeapRet[addr].toString(16));
		}
	}
}