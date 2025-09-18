function [dataOut,validOut] = hdlDCBlocker(dataIn,validIn)
%hdlDCBlocker
% Process one sample of data using the dsphdl.BiquadFilter System object 
% and subtract the filter output from the input signal. 
%
% dataIn is a fixed-point scalar value. 
% validIn is a Boolean scalar value.
%
% You can generate HDL code from this function.
    persistent dcb
    persistent match_delay
    if isempty(dcb)
        % created with : 
        %    filterOrder = 6;   
        %    normalizedBandwidth = 0.001; 
        %    passbandRipple = 0.1;   
        %    stopbandAtten  = 60; 
        %    [z,p,k] = ellip(filterOrder,passbandRipple,stopbandAtten,normalizedBandwidth);
        %    [sos,g] = zp2sos(z,p,k);
        sos =  [ 1  -1.999722603795258  1  1  -1.996966921747073  0.996970384830556
                 1  -1.999958253432398  1  1  -1.998230761471139  0.998238515958742
                 1  -1.999975040895448  1  1  -1.999468743777808  0.999479603410253 ];
        g = 9.974265048748800e-04;

        num = sos(:,1:3);
        den = sos(:,4:6);
        dcb = dsphdl.BiquadFilter(Numerator = num, ...
            Denominator = den, ...
            ScaleValues = g  , ...
            NumeratorDataType = "Custom", ...
            DenominatorDataType = "Custom", ...
            ScaleValuesDataType = "Custom", ...
            AccumulatorDataType = "Custom", ...
            OutputDataType = "Custom", ...
            CustomNumeratorDataType = numerictype(1,20,18), ...
            CustomDenominatorDataType = numerictype(1,20,18), ...
            CustomScaleValuesDataType = numerictype(1,20,19), ...
            CustomAccumulatorDataType = numerictype(1,60,40), ...
            CustomOutputDataType = numerictype(1,60,40) ...
            );
        match_delay = dsp.Delay(28);
    end
    [filtOut,validOut] = dcb(dataIn,validIn);  
    dataOut = match_delay(dataIn) - filtOut;

end

% Copyright 2024 The MathWorks, Inc. 
