% MATLAB_CODER_AVG_SCRIPT   Generate MEX-function moving_avg_mex from
% moving_avg, moving_avg.
% 
% Script generated from project 'matlab_coder_avg.coderprj' on 03-Oct-2025.
% 
% See also CODER, CODER.CONFIG, CODER.TYPEOF, CODEGEN.

%% Create configuration object of class 'coder.MexCodeConfig'.
cfg = coder.config("mex");
cfg.TargetLang = "C";
cfg.DynamicMemoryAllocationInterface = "Auto";
cfg.DynamicMemoryAllocationThreshold = 65536;
cfg.InlineBetweenMathWorksFunctions = "Speed";
cfg.InlineBetweenUserAndMathWorksFunctions = "Speed";
cfg.InlineBetweenUserFunctions = "Speed";
cfg.UsePrecompiledLibraries = "Prefer";
cfg.CppPreserveClasses = true;
cfg.EnableOpenMP = true;
cfg.ResponsivenessChecks = true;
%% Define global types and initial values.
globalVariables = cell(2, 2);
globalVariables{1,1} = coder.newtype("uint32", [1 1], [0 0]);
globalVariables{1,2} = [];
globalVariables{2,1} = coder.newtype("double", [1 Inf], [0 1]);
globalVariables{2,2} = [];

%% Invoke MATLAB Coder.
codegen -config cfg -globals {'g1', globalVariables{1,1}, 'g2', globalVariables{2,1}} ...
    moving_avg ...
    moving_avg