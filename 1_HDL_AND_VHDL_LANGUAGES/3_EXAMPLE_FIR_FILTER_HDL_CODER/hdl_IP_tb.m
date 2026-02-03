%Testbench generated using HDL IP Designer
% generate input stimulus for DUT
%% Parâmetros
numSamples = 2000;    % número de amostras

fs = 48000;          % frequência de amostragem (Hz)
t  = (0:numSamples-1)'/fs;

f1 = 1000;            % frequência da primeira senoide (Hz)
f2 = 5000;            % frequência da segunda senoide (Hz)

A1 = 0.8;            % amplitude 1
A2 = 0.5;            % amplitude 2

%% Geração dos sinais senoidais
x1 = A1 * sin(2*pi*f1*t);
x2 = A2 * sin(2*pi*f2*t);
% Sinal composto
x = x1 + x2;

%% Conversão para fix‑point
% Aqui usamos signed, wordlength=16, fraclength=15
testbench.data = fi(x, true, 16, 15);

data = testbench.data ;
NumDim = length(size( data ));
NumSamples = size( data ,1);
SamplesPerFrame = 1;
NumChannels = size( data ,2);
valid = true(1,NumSamples);
dataIn = data;
validIn = valid;
 
% call DUT with stimulus and save output
    for ii =  1 :1:NumSamples
    [dataOut(ii), validOut(ii)] = hdl_IP(dataIn(ii), validIn(ii));
    end
    
