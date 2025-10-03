function [f_out] = f_read_file(filename, delimiter)
% Open the file
    
    fileID = fopen(filename, 'r');
    
    if fileID == -1
        error('Failed to open file: %s', filename);
    end

    % Define the format string based on your data types.
    % Example for two columns of doubles separated by the specified delimiter.
    formatSpec = ['%f', delimiter, '%f']; 

    % Read the data
    dataCell = textscan(fileID, formatSpec, 'Delimiter', delimiter);

    % Close the file
    fclose(fileID);

    % Convert cell array to a matrix if all data is numeric
    f_out = cell2mat(dataCell);

end