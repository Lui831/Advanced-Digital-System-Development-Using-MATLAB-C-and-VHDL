% MATLAB_CODER_AVG_SCRIPT   Generate static library moving_avg from moving_avg.
% 
% Script generated from project 'matlab_coder_avg.coderprj' on 03-Oct-2025.
% 
% See also CODER, CODER.CONFIG, CODER.TYPEOF, CODEGEN.

%% Create configuration object of class 'coder.EmbeddedCodeConfig'.
cfg = coder.config("lib", "ecoder", true);
cfg.OutputType = "lib";
cfg.GenerateReport = true;
cfg.GenCodeOnly = true;
%% Invoke MATLAB Coder.
codegen -config cfg moving_avg