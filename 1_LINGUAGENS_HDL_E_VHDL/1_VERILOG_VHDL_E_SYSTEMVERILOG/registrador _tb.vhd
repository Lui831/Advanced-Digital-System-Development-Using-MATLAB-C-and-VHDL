library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity register_top_level is
    Port (
        clk     : in  STD_LOGIC;
        reset   : in  STD_LOGIC;
        input   : in  STD_LOGIC_VECTOR(0 to 7); -- 8 bits LITTLE ENDIAN
        output   : out STD_LOGIC_VECTOR(0 to 7)  -- 8 bits LITTLE ENDIAN
    );
end register_top_level;

architecture Behavioral of register_top_level is

signal s_output: std_logic_vector(0 to 7);


begin
processor_register:  process(clk, reset)
     begin
        if reset = '1' then
            s_output <= (others => '0');
        elsif rising_edge(clk) then -- or event'clk and clk='1' then
            s_output<= input; 
        end if;
    end process;

output <= s_output;


end Behavioral;

