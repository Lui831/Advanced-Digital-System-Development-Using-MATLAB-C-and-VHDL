
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;


entity Counter is
    port (
        clk     : in  std_logic;
        reset   : in  std_logic;
        enable  : in  std_logic;
        count   : out std_logic_vector(3 downto 0)
    );
end entity Counter;     



architecture Behavioral of Counter is
    signal counter_reg : integer 0 to 7 := (others => '0');   


process_counter:  process(clk, reset)
    begin       
        if reset = '1' then
            counter_reg <= (others => '0');   
        elsif rising_edge(clk) then
            if enable = '1' then
                counter_reg <= std_logic_vector(counter_reg + 1);   
            end if;
        end if;
    end process process_counter;    

  count <= std_logic_vector(counter_reg);     

end architecture Behavioral;