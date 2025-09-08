
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;


entity Counter_syc_tb is
end entity Counter_syc_tb;     



architecture Behavioral of Counter_syc_tb is
   
component Counter_syc is
    port (
        clk     : in  std_logic;
        reset   : in  std_logic;
        enable  : in  std_logic;
        count   : out std_logic_vector(3 downto 0)
    );
end component Counter_syc;     
   
   
   
signal s_rst : std_logic:='0';
signal s_clk : std_logic:='0';
signal s_enable : std_logic:='0';
signal s_count : std_logic_vector(3 downto 0):=(others=>'0');

    
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


    process_enable: process
       begin
         s_enable<='0';
         wait for  50 ns; 
         s_enable<='1';
         wait;
    end process process_enable;

 
inst_counter_syc:component Counter_syc
  port map (
        clk => s_clk ,
        reset => s_rst, 
        enable=>s_enable,
        count=>s_count  
     ); 



end architecture Behavioral;    