import subprocess
from datetime import datetime
import os
import logging
from traffic_gatherer.src.process import process_tshark_output, create_flows


OUTPUT_DIR = "/app/shared"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
pcap_file = os.path.join(OUTPUT_DIR, f"traffic_{timestamp}.pcap")
logger = logging.getLogger("uvicorn")
    
def gather_traffic(duration: int) -> str:
    """
    Gather network traffic using tcpdump and save it to a PCAP file.

    Args:
        duration (int): Duration in seconds for which to gather traffic.

    Returns:
        str: Path to the saved PCAP file.
    """
    command = [
        "timeout", f"{duration}s",
        "tshark",
        "-i", "wlo1",
        "-w", pcap_file,
    ]

    os.chmod(OUTPUT_DIR, 0o777)  

    logger.info(f"Iniciando captura de tráfico durante {duration} segundos...")
    proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if proc.returncode not in (0, 124):
        logger.error(f"tshark falló con código {proc.returncode}")
        logger.error(proc.stderr.decode())
        raise RuntimeError(f"tcpdump falló: código {proc.returncode}")
    else:
        logger.info("tshark terminó correctamente (timeout o éxito)")
        logger.info(proc.stderr.decode())

    os.chmod(pcap_file, 0o777)

    path = create_flows(pcap_file)

    process_tshark_output(path)

    return pcap_file
