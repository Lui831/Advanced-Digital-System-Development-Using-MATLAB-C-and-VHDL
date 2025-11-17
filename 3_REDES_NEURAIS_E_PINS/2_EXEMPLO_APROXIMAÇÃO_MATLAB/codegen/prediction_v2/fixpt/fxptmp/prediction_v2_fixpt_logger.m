% loggingMode - mode of operation : either read or log
%#codegen
%#internal
function loggedData = prediction_v2_fixpt_logger(varargin)
    coder.inline( 'never' );
    coder.extrinsic( 'MException', 'throw' );
    persistent iterCount
    if isempty( iterCount )
        iterCount = 0;
    end
    if nargin>0
        % Log the data.
        x_TB_logger( varargin{ 1 } );
        w0_TB_logger( varargin{ 2 } );
        b0_TB_logger( varargin{ 3 } );
        w1_TB_logger( varargin{ 4 } );
        b1_TB_logger( varargin{ 5 } );
        y_TB_logger( varargin{ 6 } );
        dydx_TB_logger( varargin{ 7 } );
        d2ydx2_TB_logger( varargin{ 8 } );
        y0_TB_logger( varargin{ 9 } );
        y1_TB_logger( varargin{ 10 } );
        iterCount = iterCount + 1;
        loggedData = [  ];
        if iterCount>=Inf
            throw( MException( 'Coder:FXPCONV:MATLABSimBailOut', 'Return early for input computation' ) );
        end
        return
    else
        % Fetch the data.
        % make sure the 'log setup' has been performed
        assert( ~isempty( iterCount ) );
        loggedData.inputs.x = x_TB_logger();
        loggedData.inputs.w0 = w0_TB_logger();
        loggedData.inputs.b0 = b0_TB_logger();
        loggedData.inputs.w1 = w1_TB_logger();
        loggedData.inputs.b1 = b1_TB_logger();
        loggedData.outputs.y = y_TB_logger();
        loggedData.outputs.dydx = dydx_TB_logger();
        loggedData.outputs.d2ydx2 = d2ydx2_TB_logger();
        loggedData.outputs.y0 = y0_TB_logger();
        loggedData.outputs.y1 = y1_TB_logger();
        loggedData.iterCount = iterCount;
    end
end
function out = x_TB_logger(v)
    coder.inline( 'never' );
    persistent p
    if nargin==1
        if isempty( p )
            if isvector( v ) || isscalar( v )
                coder.varsize( 'p' );
            else
                assert( ndims( v )<=3 );
                % 3D: row, col, no. samples + 4D: row, col, depth , no. of samples
                if ndims( v )==2
                    coder.varsize( 'p', [ Inf, Inf, Inf ], [ true, true, true ] );
                else
                    coder.varsize( 'p', [ Inf, Inf, Inf, Inf ], [ true, true, true, true ] );
                end
            end
            p = loggableValue( v );
        elseif isvector( v ) || isscalar( v )
            if isrow( v )
                p = [ p, loggableValue( v ) ];
            else
                %col, scalar..
                p = [ p; loggableValue( v ) ];
            end
        else
            if ndims( v )==2  % row, col, no. of samples 
                p = cat( 3, p, loggableValue( v ) );
            else  % row, col, depth , no. of samples
                p = cat( 4, p, loggableValue( v ) );
            end
        end
    else
        assert( ~isempty( p ) );
        out = p;
        p( : ) = [  ];
    end
end
function out = w0_TB_logger(v)
    coder.inline( 'never' );
    persistent p
    if nargin==1
        if isempty( p )
            if isvector( v ) || isscalar( v )
                coder.varsize( 'p' );
            else
                assert( ndims( v )<=3 );
                % 3D: row, col, no. samples + 4D: row, col, depth , no. of samples
                if ndims( v )==2
                    coder.varsize( 'p', [ Inf, Inf, Inf ], [ true, true, true ] );
                else
                    coder.varsize( 'p', [ Inf, Inf, Inf, Inf ], [ true, true, true, true ] );
                end
            end
            p = loggableValue( v );
        elseif isvector( v ) || isscalar( v )
            if isrow( v )
                p = [ p, loggableValue( v ) ];
            else
                %col, scalar..
                p = [ p; loggableValue( v ) ];
            end
        else
            if ndims( v )==2  % row, col, no. of samples 
                p = cat( 3, p, loggableValue( v ) );
            else  % row, col, depth , no. of samples
                p = cat( 4, p, loggableValue( v ) );
            end
        end
    else
        assert( ~isempty( p ) );
        out = p;
        p( : ) = [  ];
    end
end
function out = b0_TB_logger(v)
    coder.inline( 'never' );
    persistent p
    if nargin==1
        if isempty( p )
            if isvector( v ) || isscalar( v )
                coder.varsize( 'p' );
            else
                assert( ndims( v )<=3 );
                % 3D: row, col, no. samples + 4D: row, col, depth , no. of samples
                if ndims( v )==2
                    coder.varsize( 'p', [ Inf, Inf, Inf ], [ true, true, true ] );
                else
                    coder.varsize( 'p', [ Inf, Inf, Inf, Inf ], [ true, true, true, true ] );
                end
            end
            p = loggableValue( v );
        elseif isvector( v ) || isscalar( v )
            if isrow( v )
                p = [ p, loggableValue( v ) ];
            else
                %col, scalar..
                p = [ p; loggableValue( v ) ];
            end
        else
            if ndims( v )==2  % row, col, no. of samples 
                p = cat( 3, p, loggableValue( v ) );
            else  % row, col, depth , no. of samples
                p = cat( 4, p, loggableValue( v ) );
            end
        end
    else
        assert( ~isempty( p ) );
        out = p;
        p( : ) = [  ];
    end
end
function out = w1_TB_logger(v)
    coder.inline( 'never' );
    persistent p
    if nargin==1
        if isempty( p )
            if isvector( v ) || isscalar( v )
                coder.varsize( 'p' );
            else
                assert( ndims( v )<=3 );
                % 3D: row, col, no. samples + 4D: row, col, depth , no. of samples
                if ndims( v )==2
                    coder.varsize( 'p', [ Inf, Inf, Inf ], [ true, true, true ] );
                else
                    coder.varsize( 'p', [ Inf, Inf, Inf, Inf ], [ true, true, true, true ] );
                end
            end
            p = loggableValue( v );
        elseif isvector( v ) || isscalar( v )
            if isrow( v )
                p = [ p, loggableValue( v ) ];
            else
                %col, scalar..
                p = [ p; loggableValue( v ) ];
            end
        else
            if ndims( v )==2  % row, col, no. of samples 
                p = cat( 3, p, loggableValue( v ) );
            else  % row, col, depth , no. of samples
                p = cat( 4, p, loggableValue( v ) );
            end
        end
    else
        assert( ~isempty( p ) );
        out = p;
        p( : ) = [  ];
    end
end
function out = b1_TB_logger(v)
    coder.inline( 'never' );
    persistent p
    if nargin==1
        if isempty( p )
            if isvector( v ) || isscalar( v )
                coder.varsize( 'p' );
            else
                assert( ndims( v )<=3 );
                % 3D: row, col, no. samples + 4D: row, col, depth , no. of samples
                if ndims( v )==2
                    coder.varsize( 'p', [ Inf, Inf, Inf ], [ true, true, true ] );
                else
                    coder.varsize( 'p', [ Inf, Inf, Inf, Inf ], [ true, true, true, true ] );
                end
            end
            p = loggableValue( v );
        elseif isvector( v ) || isscalar( v )
            if isrow( v )
                p = [ p, loggableValue( v ) ];
            else
                %col, scalar..
                p = [ p; loggableValue( v ) ];
            end
        else
            if ndims( v )==2  % row, col, no. of samples 
                p = cat( 3, p, loggableValue( v ) );
            else  % row, col, depth , no. of samples
                p = cat( 4, p, loggableValue( v ) );
            end
        end
    else
        assert( ~isempty( p ) );
        out = p;
        p( : ) = [  ];
    end
end
function out = y_TB_logger(v)
    coder.inline( 'never' );
    persistent p
    if nargin==1
        if isempty( p )
            if isvector( v ) || isscalar( v )
                coder.varsize( 'p' );
            else
                assert( ndims( v )<=3 );
                % 3D: row, col, no. samples + 4D: row, col, depth , no. of samples
                if ndims( v )==2
                    coder.varsize( 'p', [ Inf, Inf, Inf ], [ true, true, true ] );
                else
                    coder.varsize( 'p', [ Inf, Inf, Inf, Inf ], [ true, true, true, true ] );
                end
            end
            p = loggableValue( v );
        elseif isvector( v ) || isscalar( v )
            if isrow( v )
                p = [ p, loggableValue( v ) ];
            else
                %col, scalar..
                p = [ p; loggableValue( v ) ];
            end
        else
            if ndims( v )==2  % row, col, no. of samples 
                p = cat( 3, p, loggableValue( v ) );
            else  % row, col, depth , no. of samples
                p = cat( 4, p, loggableValue( v ) );
            end
        end
    else
        assert( ~isempty( p ) );
        out = p;
        p( : ) = [  ];
    end
end
function out = dydx_TB_logger(v)
    coder.inline( 'never' );
    persistent p
    if nargin==1
        if isempty( p )
            if isvector( v ) || isscalar( v )
                coder.varsize( 'p' );
            else
                assert( ndims( v )<=3 );
                % 3D: row, col, no. samples + 4D: row, col, depth , no. of samples
                if ndims( v )==2
                    coder.varsize( 'p', [ Inf, Inf, Inf ], [ true, true, true ] );
                else
                    coder.varsize( 'p', [ Inf, Inf, Inf, Inf ], [ true, true, true, true ] );
                end
            end
            p = loggableValue( v );
        elseif isvector( v ) || isscalar( v )
            if isrow( v )
                p = [ p, loggableValue( v ) ];
            else
                %col, scalar..
                p = [ p; loggableValue( v ) ];
            end
        else
            if ndims( v )==2  % row, col, no. of samples 
                p = cat( 3, p, loggableValue( v ) );
            else  % row, col, depth , no. of samples
                p = cat( 4, p, loggableValue( v ) );
            end
        end
    else
        assert( ~isempty( p ) );
        out = p;
        p( : ) = [  ];
    end
end
function out = d2ydx2_TB_logger(v)
    coder.inline( 'never' );
    persistent p
    if nargin==1
        if isempty( p )
            if isvector( v ) || isscalar( v )
                coder.varsize( 'p' );
            else
                assert( ndims( v )<=3 );
                % 3D: row, col, no. samples + 4D: row, col, depth , no. of samples
                if ndims( v )==2
                    coder.varsize( 'p', [ Inf, Inf, Inf ], [ true, true, true ] );
                else
                    coder.varsize( 'p', [ Inf, Inf, Inf, Inf ], [ true, true, true, true ] );
                end
            end
            p = loggableValue( v );
        elseif isvector( v ) || isscalar( v )
            if isrow( v )
                p = [ p, loggableValue( v ) ];
            else
                %col, scalar..
                p = [ p; loggableValue( v ) ];
            end
        else
            if ndims( v )==2  % row, col, no. of samples 
                p = cat( 3, p, loggableValue( v ) );
            else  % row, col, depth , no. of samples
                p = cat( 4, p, loggableValue( v ) );
            end
        end
    else
        assert( ~isempty( p ) );
        out = p;
        p( : ) = [  ];
    end
end
function out = y0_TB_logger(v)
    coder.inline( 'never' );
    persistent p
    if nargin==1
        if isempty( p )
            if isvector( v ) || isscalar( v )
                coder.varsize( 'p' );
            else
                assert( ndims( v )<=3 );
                % 3D: row, col, no. samples + 4D: row, col, depth , no. of samples
                if ndims( v )==2
                    coder.varsize( 'p', [ Inf, Inf, Inf ], [ true, true, true ] );
                else
                    coder.varsize( 'p', [ Inf, Inf, Inf, Inf ], [ true, true, true, true ] );
                end
            end
            p = loggableValue( v );
        elseif isvector( v ) || isscalar( v )
            if isrow( v )
                p = [ p, loggableValue( v ) ];
            else
                %col, scalar..
                p = [ p; loggableValue( v ) ];
            end
        else
            if ndims( v )==2  % row, col, no. of samples 
                p = cat( 3, p, loggableValue( v ) );
            else  % row, col, depth , no. of samples
                p = cat( 4, p, loggableValue( v ) );
            end
        end
    else
        assert( ~isempty( p ) );
        out = p;
        p( : ) = [  ];
    end
end
function out = y1_TB_logger(v)
    coder.inline( 'never' );
    persistent p
    if nargin==1
        if isempty( p )
            if isvector( v ) || isscalar( v )
                coder.varsize( 'p' );
            else
                assert( ndims( v )<=3 );
                % 3D: row, col, no. samples + 4D: row, col, depth , no. of samples
                if ndims( v )==2
                    coder.varsize( 'p', [ Inf, Inf, Inf ], [ true, true, true ] );
                else
                    coder.varsize( 'p', [ Inf, Inf, Inf, Inf ], [ true, true, true, true ] );
                end
            end
            p = loggableValue( v );
        elseif isvector( v ) || isscalar( v )
            if isrow( v )
                p = [ p, loggableValue( v ) ];
            else
                %col, scalar..
                p = [ p; loggableValue( v ) ];
            end
        else
            if ndims( v )==2  % row, col, no. of samples 
                p = cat( 3, p, loggableValue( v ) );
            else  % row, col, depth , no. of samples
                p = cat( 4, p, loggableValue( v ) );
            end
        end
    else
        assert( ~isempty( p ) );
        out = p;
        p( : ) = [  ];
    end
end
function out = loggableValue(in)
    coder.inline( 'always' );
    if isenum( in )
        out = double( in );
    else
        out = in;
    end
end
