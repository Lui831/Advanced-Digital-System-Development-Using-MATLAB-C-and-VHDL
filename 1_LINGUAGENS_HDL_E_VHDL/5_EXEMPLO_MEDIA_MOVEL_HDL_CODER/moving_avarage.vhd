library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity moving_avarage is
    Port (
        clk     : in  STD_LOGIC;
        rst     : in  STD_LOGIC;
        inputA  : in  STD_LOGIC_VECTOR(7 downto 0); -- 8 bits
        avarage : out STD_LOGIC_VECTOR(7 downto 0)  -- 8 bits
    );
end entity moving_avarage;

architecture Behavioral of moving_avarage is

    type bufferA is array(0 to 3) of unsigned(7 downto 0); --memory sram  for 4 samples
    signal m_bufferA :bufferA;
    signal sum   : unsigned(9 downto 0); --  4 * 255 = 1020

begin
   

   process(clk, rst)
     begin
        if rst = '1' then
            m_bufferA(0) <= (others => '0');
            m_bufferA(1) <= (others => '0');
            m_bufferA(2) <= (others => '0');
            m_bufferA(3) <= (others => '0');
            sum       <= (others => '0');
            avarage   <= (others => '0');
        elsif rising_edge(clk) then
            -- shift the buffer
            m_bufferA(3) <= m_bufferA(2);
            m_bufferA(2) <= m_bufferA(1);
            m_bufferA(1) <= m_bufferA(0);
            m_bufferA(0) <= unsigned(inputA);

            -- sum the values in the buffer
            sum <= ("00" & m_bufferA(0)) + ("00" & m_bufferA(1)) + ("00" & m_bufferA(2)) + ("00" & m_bufferA(3));

            -- avarage calculation
            avarage <= std_logic_vector(sum(9 downto 2));   -- sum >> 4
        end if;
    end process;

end architecture Behavioral;
