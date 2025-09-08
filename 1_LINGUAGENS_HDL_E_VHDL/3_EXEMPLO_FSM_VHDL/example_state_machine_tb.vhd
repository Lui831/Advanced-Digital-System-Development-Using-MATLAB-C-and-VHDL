
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;


entity example_state_machine_tb is
end entity example_state_machine_tb;     



architecture Behavioral of example_state_machine_tb is
   
component example_state_machine is
    port (
        clk     : in  STD_LOGIC;
        rst   : in  STD_LOGIC;
        input   : in  STD_LOGIC;
        output  : out STD_LOGIC_VECTOR(2 downto 0) -- little-endian output
    );
end component example_state_machine;     
   
   
   
signal s_rst   : std_logic:='0';
signal s_clk   : std_logic:='0';
signal s_input : std_logic:='0';
signal s_count : std_logic_vector(2 downto 0):=(others=>'0');

    
begin

    process_reset : process
        begin
           s_rst<= '1';
           wait for 20 ns;
           s_rst<='0';
           wait;
    end process process_reset;


    process_clk : process
        begin
              s_clk<='0';
              wait for 10 ns;
              s_clk <= '1'; 
              wait for 10 ns;
     end process process_clk;


    process_input: process
       begin
         s_input<='0';
         wait for  50 ns; 
         s_input<='1';
         wait;
    end process process_input;

 
inst_example_state_machine : component example_state_machine
  port map (
         clk    => s_clk,
         rst => s_rst,
         input  => s_input,
         output => s_count
     ); 



end architecture Behavioral;    