library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use IEEE.STD_LOGIC_ARITH.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;    
use work.rng_lib.all;

entity moving_avarage_tb is
end entity moving_avarage_tb;

architecture Behavioral of moving_avarage_tb is

signal s_rst       : std_logic:='0';
signal s_clk       : std_logic:='0';
signal s_inputA    : std_logic_vector(7 downto 0):=(others=>'0');
signal s_avg_out   : std_logic_vector(7 downto 0):=(others=>'0');

component moving_avarage is
    port (
        clk     : in  std_logic;
        rst     : in  std_logic;
        inputA  : in std_logic_vector(7 downto 0);
        avarage : out std_logic_vector(7 downto 0)
    );
end component moving_avarage;

begin
  
  
process_rand :  process(s_rst, s_clk)
	variable r_uni : rand_var;
    	variable r : real;
    	variable i : integer range 0 to 255 := 0;      
    begin  
     if s_rst ='1' then
        r:=0.0;
        i:=0;
        s_inputA <= (others => '0');
        r_uni := init_uniform(2, 5, 10, 0.0, 255.0);
     elsif rising_edge(s_clk) then  
        r := r_uni.rnd; -- r is a real
        r_uni := rand(r_uni);       
        i := integer(r_uni.rnd); -- i is an integer       
        s_inputA <= std_logic_vector(to_unsigned(i, s_inputA'length));
     end if;
end process process_rand;

      process_reset : process
        begin
           s_rst<= '1';
           wait for 25 ns;
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


    

 
inst_moving_avarage: component moving_avarage
  port map (
        clk => s_clk,
        rst  => s_rst,
        inputA => s_inputA,
        avarage => s_avg_out
     ); 


end architecture Behavioral;
