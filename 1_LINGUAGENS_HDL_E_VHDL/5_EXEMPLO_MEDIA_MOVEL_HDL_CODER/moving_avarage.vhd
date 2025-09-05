library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity moving_avarage is
    Port (
        clk     : in  STD_LOGIC;
        reset   : in  STD_LOGIC;
        input   : in  STD_LOGIC_VECTOR(7 downto 0); -- 8 bits
        avarage   : out STD_LOGIC_VECTOR(7 downto 0)  -- 8 bits
    );
end moving_avarage;

architecture Behavioral of moving_avarage is

    signal buffer : array(0 to 3) of unsigned(7 downto 0); --memory sram  for 4 samples
    signal sum   : unsigned(9 downto 0); --  4 * 255 = 1020

begin
   

   process(clk, reset)
     begin
        if reset = '1' then
            buffer(0) <= (others => '0');
            buffer(1) <= (others => '0');
            buffer(2) <= (others => '0');
            buffer(3) <= (others => '0');
            sum       <= (others => '0');
            avarage   <= (others => '0');
        elsif rising_edge(clk) then
            -- shift the buffer
            buffer(3) <= buffer(2);
            buffer(2) <= buffer(1);
            buffer(1) <= buffer(0);
            buffer(0) <= unsigned(input);

            -- sum the values in the buffer
            sum <= buffer(0) + buffer(1) + buffer(2) + buffer(3);

            -- avarage calculation
            avarage <= std_logic_vector(sum(9 downto 2));   -- sum >> 4
        end if;
    end process;
end Behavioral;
