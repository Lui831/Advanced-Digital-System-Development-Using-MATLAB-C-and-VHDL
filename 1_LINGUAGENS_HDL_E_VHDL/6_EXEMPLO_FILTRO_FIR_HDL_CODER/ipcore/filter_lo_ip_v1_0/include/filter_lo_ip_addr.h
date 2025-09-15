/*
 * File Name:         C:\curso_HDL_Vanderlei\Advanced-Digital-System-Development-Using-MATLAB-C-and-VHDL\1_LINGUAGENS_HDL_E_VHDL\6_EXEMPLO_FILTRO_FIR_HDL_CODER\ipcore\filter_lo_ip_v1_0\include\filter_lo_ip_addr.h
 * Description:       C Header File
 * Created:           2025-09-14 18:44:20
*/

#ifndef FILTER_LO_IP_H_
#define FILTER_LO_IP_H_

#define  IPCore_Reset_filter_lo_ip       0x0  //write 0x1 to bit 0 to reset IP core
#define  IPCore_Enable_filter_lo_ip      0x4  //enabled (by default) when bit 0 is 0x1
#define  IPCore_Timestamp_filter_lo_ip   0x8  //contains unique IP timestamp (yymmddHHMM): 2509141844

#endif /* FILTER_LO_IP_H_ */
