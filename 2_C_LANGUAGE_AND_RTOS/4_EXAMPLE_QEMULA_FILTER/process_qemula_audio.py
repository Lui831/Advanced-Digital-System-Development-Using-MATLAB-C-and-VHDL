#!/usr/bin/env python3
"""
Le dados chirp do Excel, toca o audio do sinal de entrada, envia cada amostra
via TCP (value + '!'), coleta o valor filtrado e toca o audio de saida.
"""

from __future__ import annotations

import argparse
import os
import re
import socket
import sys
import tempfile
import time
import wave
from typing import Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd

try:
    import sounddevice as sd  # type: ignore
except Exception:
    sd = None

try:
    import winsound  # type: ignore
except Exception:
    winsound = None

FILTER_RE = re.compile(r"DEBUG: Valor filtrado: ([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)")
INIT_PORT = 5054


def load_chirp_values(path: str) -> Tuple[np.ndarray, str]:
    df = pd.read_excel(path)
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if numeric_cols:
        col = numeric_cols[0]
        values = df[col].dropna().to_numpy(dtype=float)
        return values, str(col)

    # Fallback: tentar converter a primeira coluna
    if len(df.columns) == 0:
        raise ValueError("Planilha sem colunas.")

    col = df.columns[0]
    series = pd.to_numeric(df[col], errors="coerce")
    if series.notna().any():
        return series.dropna().to_numpy(dtype=float), str(col)

    raise ValueError("Nenhuma coluna numerica encontrada no arquivo.")


def normalize_audio(values: np.ndarray) -> np.ndarray:
    if values.size == 0:
        return values.astype(np.float32)
    max_val = float(np.max(np.abs(values)))
    if max_val == 0:
        return values.astype(np.float32)
    return (values / max_val).astype(np.float32)


def write_wav(path: str, samples: np.ndarray, sample_rate: int) -> None:
    samples = np.clip(samples, -1.0, 1.0)
    int16 = (samples * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(int16.tobytes())


def play_audio(samples: np.ndarray, sample_rate: int, label: str, keep_wav: bool) -> Optional[str]:
    if samples.size == 0:
        print(f"{label}: sem amostras, pulando.")
        return None

    if sd is not None:
        print(f"{label}: tocando com sounddevice...")
        sd.play(samples, sample_rate, blocking=True)
        return None

    fd, wav_path = tempfile.mkstemp(suffix=".wav", prefix="chirp_")
    os.close(fd)
    write_wav(wav_path, samples, sample_rate)

    if winsound is not None:
        print(f"{label}: tocando com winsound...")
        winsound.PlaySound(wav_path, winsound.SND_FILENAME)
    else:
        print(f"{label}: playback indisponivel, WAV salvo em: {wav_path}")
        keep_wav = True

    if not keep_wav:
        try:
            os.remove(wav_path)
        except OSError:
            pass
        return None

    return wav_path


def send_value_to_server(value: float, server: str, port: int, timeout: float) -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((server, port))
        message = f"{value}!"
        sock.send(message.encode("utf-8"))
        response = ""
        while True:
            data = sock.recv(1024).decode("utf-8")
            if not data:
                break
            response += data
            if "DEBUG: Processamento concluido" in response:
                break
        return response
    finally:
        sock.close()


def parse_filtered_value(response: str) -> Optional[float]:
    match = FILTER_RE.search(response)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def init_container_client(server: str, timeout: float) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((server, INIT_PORT))
    finally:
        sock.close()


def load_filtered_values(path: str) -> np.ndarray:
    df = pd.read_excel(path)
    if "Valor_Filtrado" in df.columns:
        series = pd.to_numeric(df["Valor_Filtrado"], errors="coerce")
        return series.dropna().to_numpy(dtype=float)
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if numeric_cols:
        series = pd.to_numeric(df[numeric_cols[0]], errors="coerce")
        return series.dropna().to_numpy(dtype=float)
    raise ValueError("Nenhuma coluna numerica encontrada no arquivo de saida.")


def send_values(
    values: Iterable[float],
    server: str,
    port: int,
    timeout: float,
    delay_ms: int,
    verbose: bool,
) -> List[Optional[float]]:
    values_list = list(values)
    total = len(values_list)
    filtered: List[Optional[float]] = []

    for i, value in enumerate(values_list):
        if verbose:
            print(f"[{i + 1:5d}/{total}] Enviando: {value}")
        elif i % 100 == 0 or i == total - 1:
            pct = (i + 1) / total * 100 if total else 100.0
            print(f"Progresso: {i + 1}/{total} ({pct:.1f}%)")

        try:
            response = send_value_to_server(value, server, port, timeout)
        except Exception as exc:
            if verbose:
                print(f"  ERRO: {exc}")
            filtered.append(None)
        else:
            if "ERRO:" in response:
                if verbose:
                    print(f"  {response}")
                filtered.append(None)
            else:
                filtered_value = parse_filtered_value(response)
                filtered.append(filtered_value)
                if verbose:
                    print(f"  Filtrado: {filtered_value}")

        if delay_ms > 0 and i < total - 1:
            time.sleep(delay_ms / 1000.0)

    return filtered


def save_results_excel(
    output_path: str, original: np.ndarray, filtered: List[Optional[float]]
) -> None:
    min_len = min(len(original), len(filtered))
    df = pd.DataFrame(
        {
            "Valor_Original": original[:min_len].tolist(),
            "Valor_Filtrado": filtered[:min_len],
        }
    )
    df.to_excel(output_path, index=False)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Envia dados chirp via TCP e toca o audio de entrada/saida."
    )
    parser.add_argument("--input", default="dados_chirp.xlsx", help="Arquivo Excel de entrada.")
    parser.add_argument(
        "--output",
        default="dados_chirp_filtrados.xlsx",
        help="Arquivo Excel de saida.",
    )
    parser.add_argument("--server", default="localhost", help="Servidor TCP.")
    parser.add_argument("--port", type=int, default=5050, help="Porta TCP.")
    parser.add_argument("--timeout", type=float, default=5.0, help="Timeout em segundos.")
    parser.add_argument("--delay-ms", type=int, default=10, help="Delay entre envios (ms).")
    parser.add_argument("--sample-rate", type=int, default=8192, help="Taxa de amostragem.")
    parser.add_argument("--no-play-input", action="store_true", help="Nao tocar audio de entrada.")
    parser.add_argument("--no-play-output", action="store_true", help="Nao tocar audio de saida.")
    parser.add_argument("--keep-wav", action="store_true", help="Manter WAV temporario.")
    parser.add_argument(
        "--only-show-audio",
        action="store_true",
        help="Apenas tocar audio de entrada e saida (sem envio TCP).",
    )
    parser.add_argument("--verbose", action="store_true", help="Log detalhado.")
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"ERRO: arquivo '{args.input}' nao encontrado.")
        return 1

    if not args.only_show_audio:
        try:
            init_container_client(args.server, args.timeout)
            print(f"Cliente inicializado em {args.server}:{INIT_PORT}")
        except Exception as exc:
            print(f"ERRO ao inicializar client na porta {INIT_PORT}: {exc}")
            return 1

    try:
        values, col = load_chirp_values(args.input)
    except Exception as exc:
        print(f"ERRO ao carregar dados: {exc}")
        return 1

    print(f"Arquivo: {args.input}")
    print(f"Coluna: {col}")
    print(f"Total de valores: {len(values)}")
    print(f"Servidor: {args.server}:{args.port}")
    print(f"Delay: {args.delay_ms}ms")

    input_audio = normalize_audio(values)
    if not args.no_play_input:
        play_audio(input_audio, args.sample_rate, "Audio de entrada", args.keep_wav)

    if args.only_show_audio:
        try:
            filtered_numeric = load_filtered_values(args.output)
            print(f"Carregado audio de saida de: {args.output}")
        except Exception as exc:
            print(f"ERRO ao carregar audio de saida: {exc}")
            return 1
    else:
        print("Enviando dados...")
        filtered_values = send_values(
            values,
            server=args.server,
            port=args.port,
            timeout=args.timeout,
            delay_ms=args.delay_ms,
            verbose=args.verbose,
        )

        try:
            save_results_excel(args.output, values, filtered_values)
            print(f"Resultados salvos em: {args.output}")
        except Exception as exc:
            print(f"Aviso: nao foi possivel salvar '{args.output}': {exc}")

        filtered_numeric = np.array(
            [v if v is not None else 0.0 for v in filtered_values], dtype=float
        )
    output_audio = normalize_audio(filtered_numeric)
    if not args.no_play_output:
        play_audio(output_audio, args.sample_rate, "Audio de saida", args.keep_wav)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
